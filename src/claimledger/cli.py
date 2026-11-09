import json
import sys
from pathlib import Path

import click

from . import dataset
from .adapters import ADAPTER_NAMES
from .compare import ClaimFileError, compare, load_claims
from .judge import judge_label, ollama_judge
from .report import render_markdown, write_report
from .runner import INDEX_TEXTS, AdapterSelfTestFailed, run, selftest

DEFAULT_DATA = Path("data") / "longmemeval_s_cleaned.json"


def _fail(message: str):
    click.echo(f"error: {message}", err=True)
    sys.exit(2)


@click.group()
def main():
    """Run an agent-memory library on a fixed LongMemEval slice and set it beside its claims."""


@main.command()
@click.option("--dest", type=click.Path(path_type=Path), default=DEFAULT_DATA, show_default=True)
def fetch(dest):
    """Download the pinned LongMemEval-S file (about 277 MB) and verify its sha256."""
    try:
        dataset.fetch(dest)
    except dataset.DatasetHashMismatch as error:
        _fail(str(error))
    click.echo(f"{dest} sha256 {dataset.DATASET_SHA256} verified")


@main.command("run")
@click.option("--adapter", "adapter_name", required=True, type=click.Choice(ADAPTER_NAMES))
@click.option("--slice", "slice_size", default=50, show_default=True, type=click.IntRange(1, dataset.MAX_SLICE))
@click.option("--seed", default=0, show_default=True, type=int)
@click.option("--k", default=5, show_default=True, type=click.Choice(["1", "3", "5", "10"]))
@click.option("--index-text", default="user_only", show_default=True, type=click.Choice(INDEX_TEXTS))
@click.option("--data", type=click.Path(path_type=Path), default=DEFAULT_DATA, show_default=True)
@click.option("--out", type=click.Path(path_type=Path), default=Path("results"), show_default=True)
@click.option("--judge-model", default=None, help="Also score answers with this local Ollama model (weaker than the paper's judge).")
def run_command(adapter_name, slice_size, seed, k, index_text, data, out, judge_model):
    """Run one adapter over a seeded slice and write a markdown and a JSON report."""
    try:
        entries = dataset.load(data)
    except FileNotFoundError:
        _fail(f"{data} not found; run `claimledger fetch` first")
    except dataset.DatasetHashMismatch as error:
        _fail(str(error))
    chosen = dataset.select_slice(entries, slice_size, seed)
    judge = ollama_judge(judge_model) if judge_model else None
    try:
        report = run(
            chosen, adapter_name, index_text=index_text, k=int(k), seed=seed,
            judge=judge, judge_label=judge_label(judge_model) if judge_model else "none",
        )
    except AdapterSelfTestFailed as error:
        _fail(str(error))
    json_path, md_path = write_report(report, out)
    click.echo(render_markdown(report))
    click.echo(f"wrote {md_path} and {json_path}")


@main.command("selftest")
@click.option("--adapter", "adapter_name", required=True, type=click.Choice(ADAPTER_NAMES))
def selftest_command(adapter_name):
    """Check an adapter on a three-session fixture before trusting any run."""
    try:
        selftest(adapter_name)
    except AdapterSelfTestFailed as error:
        _fail(str(error))
    click.echo(f"adapter {adapter_name} passed the fixture")


@main.command("compare")
@click.option("--claims", required=True, type=click.Path(exists=True, path_type=Path))
@click.option("--report", "report_path", required=True, type=click.Path(exists=True, path_type=Path))
@click.option("--baseline", "baseline_paths", multiple=True, type=click.Path(exists=True, path_type=Path))
def compare_command(claims, report_path, baseline_paths):
    """Render claimed versus measured for every claim in a claim file."""
    try:
        claims_doc = load_claims(claims)
    except ClaimFileError as error:
        _fail(str(error))
    report = json.loads(report_path.read_text(encoding="utf-8"))
    baselines = [json.loads(p.read_text(encoding="utf-8")) for p in baseline_paths]
    click.echo(compare(claims_doc, report, baselines))

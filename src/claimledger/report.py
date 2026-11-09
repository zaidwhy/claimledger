"""Markdown and JSON rendering of a run."""
import json
from pathlib import Path

SETTING_ORDER = [
    "adapter", "library", "library_version", "pipeline", "dataset", "dataset_sha256", "metric", "k",
    "index_text", "granularity", "judge", "slice_size", "seed", "claimledger_version",
]


def pct(value: float) -> str:
    return f"{value * 100:.1f}%"


def interval_row(label: str, cell: dict) -> str:
    return (
        f"| {label} | {pct(cell['rate'])} | {cell['hits']}/{cell['n']} | "
        f"{pct(cell['ci_low'])} to {pct(cell['ci_high'])} |"
    )


def render_markdown(report: dict) -> str:
    settings = report["settings"]
    k = str(settings["k"])
    headline = report["recall_any"][k]
    lines = [
        f"# claimledger report: {settings['adapter']}",
        "",
        f"Retrieval-only recall_any@{k}: **{pct(headline['rate'])}** "
        f"({headline['hits']}/{headline['n']}, 95% Wilson interval "
        f"{pct(headline['ci_low'])} to {pct(headline['ci_high'])}). No LLM was involved in this number.",
        "",
        "## Settings",
        "",
        "| setting | value |",
        "|---|---|",
    ]
    for key in SETTING_ORDER:
        lines.append(f"| {key} | {settings[key]} |")
    lines += [
        "",
        f"Questions scored: {report['questions_scored']} of {settings['slice_size']} "
        f"in the slice. Adapter errors: {len(report['adapter_errors'])}.",
    ]
    if report["adapter_errors"]:
        lines += ["", "Adapter errors (these questions are not scored; compare will refuse this report):", ""]
        lines += [f"- {e['question_id']}: {e['error']}" for e in report["adapter_errors"][:10]]
    lines += [
        "",
        "## Retrieval recall (session level)",
        "",
        "| metric | rate | hits | 95% interval |",
        "|---|---|---|---|",
    ]
    for kk in settings["ks_measured"]:
        lines.append(interval_row(f"recall_any@{kk}", report["recall_any"][str(kk)]))
    for kk in settings["ks_measured"]:
        lines.append(interval_row(f"recall_all@{kk}", report["recall_all"][str(kk)]))
    lines += [
        "",
        f"## recall_any@{k} by question type",
        "",
        "| type | rate | hits | 95% interval |",
        "|---|---|---|---|",
    ]
    for qtype, cells in report["by_question_type"].items():
        lines.append(interval_row(qtype, cells[k]))
    lines += ["", "Small cells have wide intervals; read the interval, not the point value.", ""]
    answer = report.get("answer_level")
    if answer:
        lines += [
            "## Answer-level (local judge, secondary)",
            "",
            f"Judge: {settings['judge']}. This judge is weaker than the GPT-4o judge used in the "
            "LongMemEval paper and these numbers are not comparable to published answer accuracy.",
            "",
            "| metric | rate | hits | 95% interval |",
            "|---|---|---|---|",
            interval_row("answer accuracy", answer),
            "",
        ]
    lines.append(f"Run time: {report['seconds']} s.")
    return "\n".join(lines) + "\n"


def write_report(report: dict, out_dir: Path) -> tuple[Path, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    s = report["settings"]
    stem = f"{s['adapter']}_n{s['slice_size']}_seed{s['seed']}_k{s['k']}"
    json_path, md_path = out_dir / f"{stem}.json", out_dir / f"{stem}.md"
    json_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    md_path.write_text(render_markdown(report), encoding="utf-8")
    return json_path, md_path

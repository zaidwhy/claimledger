"""Recount a vendor's own per-question result file, so a headline can be checked against the file published beside it.

No model is called. The file is read as published; every verdict label is counted, and rows the vendor marked
ERROR are reported both ways (as wrong, and excluded) because the headline rarely says which it used.
"""
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

PASS_LABELS = {"PASS", "CORRECT"}
ERROR_LABELS = {"ERROR"}
# A vendor result file larger than this is not a per-question file of a 500 or 1540 question benchmark.
MAX_FILE_BYTES = 200 * 1024 * 1024


class TallyError(Exception):
    pass


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def load_mem0(path: Path) -> dict:
    """mem0ai/memory-benchmarks format: metadata, evaluations[*].cutoff_results[cutoff].judgment."""
    size = Path(path).stat().st_size
    if size > MAX_FILE_BYTES:
        raise TallyError(f"{path}: {size} bytes is over the {MAX_FILE_BYTES} byte limit")
    doc = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(doc, dict) or "evaluations" not in doc:
        raise TallyError(f"{path}: no 'evaluations' list; not a mem0 memory-benchmarks result file")
    return doc


def _group_key(row: dict) -> str:
    return str(row.get("question_type") or row.get("category_name") or row.get("category") or "unlabelled")


def tally_mem0(doc: dict) -> dict:
    rows = doc["evaluations"]
    cutoffs = sorted({cutoff for row in rows for cutoff in row.get("cutoff_results", {})})
    if not cutoffs:
        raise TallyError("no row has cutoff_results; nothing to count")
    per_cutoff = {}
    for cutoff in cutoffs:
        labels = Counter()
        by_group = defaultdict(Counter)
        missing = 0
        for row in rows:
            verdict = row.get("cutoff_results", {}).get(cutoff)
            if verdict is None:
                missing += 1
                continue
            label = str(verdict.get("judgment", "")).upper() or "NO_JUDGMENT"
            labels[label] += 1
            by_group[_group_key(row)][label] += 1
        passed = sum(labels[label] for label in PASS_LABELS)
        errors = sum(labels[label] for label in ERROR_LABELS)
        judged = sum(labels.values())
        per_cutoff[cutoff] = {
            "labels": dict(labels),
            "passed": passed,
            "questions": len(rows),
            "missing": missing,
            "errors": errors,
            # Denominator is every question: an ERROR row or a row with no verdict counts as not passed.
            "accuracy_errors_as_wrong": passed / len(rows) if rows else 0.0,
            "accuracy_errors_excluded": passed / (judged - errors) if judged - errors else 0.0,
            "by_group": {
                group: {"passed": sum(c[label] for label in PASS_LABELS), "n": sum(c.values())}
                for group, c in sorted(by_group.items())
            },
        }
    return {"metadata": doc.get("metadata", {}), "cutoffs": per_cutoff}


def render_tally(path: Path, result: dict) -> str:
    lines = [f"# tally: {Path(path).name}", "", f"sha256 `{file_sha256(path)}`", ""]
    meta = result["metadata"]
    for key in sorted(meta):
        value = meta[key]
        if isinstance(value, str) and len(value) > 120:
            value = value[:117] + "..."
        lines.append(f"- {key}: {value}")
    for cutoff, cell in result["cutoffs"].items():
        lines += [
            "",
            f"## {cutoff}",
            "",
            f"Passed {cell['passed']} of {cell['questions']} "
            f"({cell['accuracy_errors_as_wrong'] * 100:.1f}% with ERROR rows counted wrong, "
            f"{cell['accuracy_errors_excluded'] * 100:.1f}% with them excluded). "
            f"Labels: {cell['labels']}. Rows with no verdict at this cutoff: {cell['missing']}.",
            "",
            "| group | passed | n |",
            "|---|---|---|",
        ]
        lines += [f"| {group} | {g['passed']} | {g['n']} |" for group, g in cell["by_group"].items()]
    return "\n".join(lines)

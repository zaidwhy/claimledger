"""Claimed versus measured, with every setting printed and a refusal when they differ."""
from pathlib import Path

import yaml

from .report import pct

# A gap is only stated when all of these agree between the claim and the run.
COMPARABLE_KEYS = ["library", "pipeline", "dataset", "metric", "k", "index_text", "granularity", "judge"]
REQUIRED_CLAIM_FIELDS = ["id", "quote", "value", "settings"]


class ClaimFileError(Exception):
    pass


def load_claims(path: Path) -> dict:
    doc = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    for field in ("library", "source", "claims"):
        if field not in doc:
            raise ClaimFileError(f"{path}: missing top-level field {field!r}")
    for claim in doc["claims"]:
        for field in REQUIRED_CLAIM_FIELDS:
            if field not in claim:
                raise ClaimFileError(f"{path}: claim {claim.get('id', '?')!r} missing field {field!r}")
        missing = [key for key in COMPARABLE_KEYS if key not in claim["settings"]]
        if missing:
            raise ClaimFileError(
                f"{path}: claim {claim['id']!r} does not state {', '.join(missing)}; "
                "a claim without its settings cannot be compared"
            )
    return doc


def setting_rows(claim_settings: dict, run_settings: dict) -> list[tuple[str, str, str, bool]]:
    rows = []
    for key in COMPARABLE_KEYS:
        claimed, measured = claim_settings[key], run_settings[key]
        rows.append((key, str(claimed), str(measured), claimed == measured))
    return rows


def _settings_table(rows) -> list[str]:
    lines = ["| setting | claimed | this run | same |", "|---|---|---|---|"]
    for key, claimed, measured, same in rows:
        lines.append(f"| {key} | {claimed} | {measured} | {'yes' if same else 'NO'} |")
    return lines


def compare_claim(claim: dict, library: str, source: dict, report: dict, baselines: list[dict]) -> str:
    run = report["settings"]
    rows = setting_rows(claim["settings"], run)
    differing = [(key, claimed, measured) for key, claimed, measured, same in rows if not same]
    lines = [
        f"### {library}: {claim['id']}",
        "",
        f"Claim: \"{claim['quote']}\" ({source['file']}, line {source['line']}, {source['url']})",
        f"Claimed value: {pct(claim['value'])}"
        + (f" on {claim['settings']['questions']} questions" if "questions" in claim["settings"] else ""),
        "",
    ]
    lines += _settings_table(rows)
    lines.append("")
    if differing:
        detail = "; ".join(f"{key} (claimed {c}, run {m})" for key, c, m in differing)
        lines.append(
            f"NOT COMPARED. The settings differ: {detail}. "
            "No gap is stated between numbers measured under different settings."
        )
    elif report["adapter_errors"]:
        lines.append(
            f"NOT COMPARED. The run had {len(report['adapter_errors'])} adapter errors, "
            "so it cannot be attributed to the library."
        )
    else:
        cell = report["recall_any"][str(claim["settings"]["k"])]
        inside = cell["ci_low"] <= claim["value"] <= cell["ci_high"]
        lines += [
            f"Measured {pct(cell['rate'])} ({cell['hits']}/{cell['n']}, 95% interval "
            f"{pct(cell['ci_low'])} to {pct(cell['ci_high'])}) on a seeded slice of "
            f"{run['slice_size']} questions (seed {run['seed']}).",
            f"The claimed {pct(claim['value'])} is {'inside' if inside else 'outside'} the measured interval.",
        ]
        if inside:
            lines.append(
                f"A slice of {cell['n']} cannot separate differences smaller than the interval width "
                f"({pct(cell['ci_high'] - cell['ci_low'])})."
            )
    for base in baselines:
        bs = base["settings"]
        kk = str(claim["settings"]["k"])
        if kk in base["recall_any"]:
            cell = base["recall_any"][kk]
            same_slice = (bs["slice_size"], bs["seed"]) == (run["slice_size"], run["seed"])
            lines.append(
                f"Baseline {bs['adapter']} ({bs['library_version']}, pipeline {bs['pipeline']}, "
                f"index_text {bs['index_text']}): recall_any@{kk} {pct(cell['rate'])} "
                f"({cell['hits']}/{cell['n']}, interval {pct(cell['ci_low'])} to {pct(cell['ci_high'])})"
                + ("" if same_slice else "; this baseline ran on a different slice") + "."
            )
    return "\n".join(lines) + "\n"


def compare(claims_doc: dict, report: dict, baselines: list[dict] | None = None) -> str:
    library, source = claims_doc["library"], claims_doc["source"]
    run = report["settings"]
    out = [
        f"# claimledger compare: {library} claims against run of {run['adapter']}",
        "",
        f"Claims source: {source['url']} at {source.get('retrieved', 'unknown date')}.",
        "",
    ]
    if run["library"] != library:
        out.append(
            f"NOT COMPARED. The claim file is for {library}; this report is from adapter "
            f"{run['adapter']} (library {run['library']}). Run the adapter for the library under test."
        )
        return "\n".join(out) + "\n"
    for claim in claims_doc["claims"]:
        out.append(compare_claim(claim, library, source, report, baselines or []))
    return "\n".join(out)

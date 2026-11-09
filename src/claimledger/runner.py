"""Run one adapter over a slice and produce the report dict."""
import time
from collections import defaultdict

from . import __version__
from .adapters import make
from .dataset import DATASET_NAME, DATASET_SHA256
from .metrics import recall_all, recall_any, wilson_interval

KS = (1, 3, 5, 10)
INDEX_TEXTS = ("user_only", "all_turns")
SCHEMA_VERSION = 1

# Three sessions and three questions with an unambiguous lexical and semantic answer.
SELFTEST_DOCS = [
    ("fx_bread", "I baked sourdough bread with a rye starter on Sunday morning."),
    ("fx_tires", "The garage said my car needs new winter tires and a brake check."),
    ("fx_lisbon", "We booked flights to Lisbon in May and a hotel near the river."),
]
SELFTEST_QUERIES = [
    ("which starter did I use for my bread", "fx_bread"),
    ("what did the garage say about my car", "fx_tires"),
    ("where are we flying in May", "fx_lisbon"),
]


class AdapterSelfTestFailed(Exception):
    pass


def session_documents(entry: dict, index_text: str) -> list[tuple[str, str]]:
    """One document per haystack session; sessions with no text are dropped."""
    if index_text not in INDEX_TEXTS:
        raise ValueError(f"index_text must be one of {INDEX_TEXTS}, got {index_text!r}")
    documents = []
    for session_id, turns in zip(entry["haystack_session_ids"], entry["haystack_sessions"]):
        if index_text == "user_only":
            text = "\n".join(turn["content"] for turn in turns if turn["role"] == "user")
        else:
            text = "\n".join(f"{turn['role']}: {turn['content']}" for turn in turns)
        if text.strip():
            documents.append((session_id, text))
    return documents


def dedupe(session_ids: list[str]) -> list[str]:
    return list(dict.fromkeys(session_ids))


def selftest(adapter_name: str) -> None:
    """Fail loudly when the adapter cannot find an obvious answer, before any library is blamed."""
    for query, expected in SELFTEST_QUERIES:
        adapter = make(adapter_name)
        try:
            adapter.ingest(SELFTEST_DOCS)
            found = dedupe(adapter.search(query, 1))
        finally:
            adapter.close()
        if found[:1] != [expected]:
            raise AdapterSelfTestFailed(
                f"adapter {adapter_name!r} returned {found[:1]} for {query!r}, expected {[expected]}. "
                "This is an adapter fault; no result from this adapter is reported."
            )


def _summary(hit_flags: list[bool]) -> dict:
    n = len(hit_flags)
    hits = sum(hit_flags)
    low, high = wilson_interval(hits, n) if n else (0.0, 0.0)
    return {"hits": hits, "n": n, "rate": hits / n if n else 0.0, "ci_low": low, "ci_high": high}


def run(
    entries: list[dict],
    adapter_name: str,
    index_text: str = "user_only",
    k: int = 5,
    seed: int = 0,
    judge=None,
    judge_label: str = "none",
    clock=time.monotonic,
) -> dict:
    selftest(adapter_name)
    probe = make(adapter_name)
    settings = {
        "dataset": DATASET_NAME,
        "dataset_sha256": DATASET_SHA256,
        "metric": "recall_any",
        "k": k,
        "ks_measured": list(KS),
        "index_text": index_text,
        "granularity": "session",
        "pipeline": probe.pipeline,
        "judge": judge_label,
        "adapter": adapter_name,
        "library": probe.library,
        "library_version": probe.library_version(),
        "slice_size": len(entries),
        "seed": seed,
        "claimledger_version": __version__,
    }
    probe.close()
    max_k = max(KS + (k,))

    per_question, errors = [], []
    flags_any = {kk: [] for kk in KS}
    flags_all = {kk: [] for kk in KS}
    by_type: dict[str, dict[int, list[bool]]] = defaultdict(lambda: {kk: [] for kk in KS})
    judged = []
    started = clock()
    for entry in entries:
        qid, qtype = entry["question_id"], entry["question_type"]
        adapter = make(adapter_name)
        try:
            documents = session_documents(entry, index_text)
            adapter.ingest(documents)
            ranked = dedupe(adapter.search(entry["question"], max_k))
        except Exception as error:  # recorded per question and surfaced in the report, never dropped
            errors.append({"question_id": qid, "error": f"{type(error).__name__}: {error}"})
            continue
        finally:
            adapter.close()
        evidence = entry["answer_session_ids"]
        row = {"question_id": qid, "question_type": qtype, "evidence": evidence, "top": ranked[:max_k]}
        for kk in KS:
            hit = recall_any(ranked, evidence, kk)
            flags_any[kk].append(hit)
            flags_all[kk].append(recall_all(ranked, evidence, kk))
            by_type[qtype][kk].append(hit)
        row["first_evidence_rank"] = next(
            (rank + 1 for rank, sid in enumerate(ranked) if sid in evidence), None
        )
        if judge is not None:
            texts = dict(documents)
            context = [texts[sid] for sid in ranked[:k] if sid in texts]
            correct = judge(entry["question"], entry["answer"], context)
            row["answer_correct"] = correct
            judged.append(correct)
        per_question.append(row)

    return {
        "schema_version": SCHEMA_VERSION,
        "settings": settings,
        "questions_scored": len(per_question),
        "adapter_errors": errors,
        "recall_any": {str(kk): _summary(flags_any[kk]) for kk in KS},
        "recall_all": {str(kk): _summary(flags_all[kk]) for kk in KS},
        "by_question_type": {
            qtype: {str(kk): _summary(flags[kk]) for kk in KS} for qtype, flags in sorted(by_type.items())
        },
        "answer_level": _summary(judged) if judge is not None else None,
        "seconds": round(clock() - started, 1),
        "question_ids": [entry["question_id"] for entry in entries],
        "per_question": per_question,
    }

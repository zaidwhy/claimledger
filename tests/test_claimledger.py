import copy
import json
from pathlib import Path

import pytest
import yaml
from click.testing import CliRunner

from claimledger import dataset
from claimledger.cli import main
from claimledger.compare import ClaimFileError, compare, load_claims
from claimledger.judge import ollama_judge, parse_verdict
from claimledger.metrics import recall_all, recall_any, wilson_interval
from claimledger.report import SETTING_ORDER, render_markdown
from claimledger.runner import AdapterSelfTestFailed, run, session_documents

CLAIMS_FILE = Path(__file__).parent.parent / "claims" / "mempalace.yaml"


# ---- recall on a hand-made fixture with known answers ----

RANKED = ["a", "b", "c", "d", "e", "f"]


@pytest.mark.parametrize(
    "evidence,k,any_hit,all_hit",
    [
        (["c"], 2, False, False),
        (["c"], 3, True, True),
        (["c", "z"], 5, True, False),
        (["a", "e"], 5, True, True),
        (["a", "e"], 4, True, False),
        (["z"], 6, False, False),
    ],
)
def test_recall_known_answers(evidence, k, any_hit, all_hit):
    assert recall_any(RANKED, evidence, k) is any_hit
    assert recall_all(RANKED, evidence, k) is all_hit


def test_wilson_interval_matches_hand_computed_values():
    low, high = wilson_interval(48, 50)
    assert (round(low, 3), round(high, 3)) == (0.865, 0.989)
    assert wilson_interval(0, 10)[0] == 0.0 and wilson_interval(10, 10)[1] == 1.0


def test_run_scores_fixture_exactly(fixture_entries):
    report = run(fixture_entries, "bm25", k=5)
    assert report["questions_scored"] == 5
    assert report["recall_any"]["1"]["hits"] == 5
    assert report["recall_any"]["5"]["rate"] == 1.0
    assert report["adapter_errors"] == []


def test_run_counts_a_miss(fixture_entries):
    wrong = copy.deepcopy(fixture_entries)
    wrong[0]["answer_session_ids"] = ["n3"]
    report = run(wrong, "bm25", k=1)
    assert report["recall_any"]["1"]["hits"] == 4
    assert report["recall_any"]["1"]["n"] == 5


def test_user_only_index_drops_assistant_text(fixture_entries):
    docs = dict(session_documents(fixture_entries[0], "user_only"))
    assert "ok" not in docs["s_cheese"].split()
    full = dict(session_documents(fixture_entries[0], "all_turns"))
    assert "assistant: ok" in full["s_cheese"]


def test_broken_adapter_is_refused_not_scored(register_broken, fixture_entries):
    with pytest.raises(AdapterSelfTestFailed, match="adapter fault"):
        run(fixture_entries, "broken")


# ---- dataset: slices and hash ----


def fake_dataset(n=40):
    return [{"question_id": f"q{i:03d}", "question_type": "t"} for i in range(n)]


def test_slice_is_deterministic_for_a_seed():
    entries = fake_dataset()
    first = [e["question_id"] for e in dataset.select_slice(entries, 10, seed=7)]
    again = [e["question_id"] for e in dataset.select_slice(entries, 10, seed=7)]
    shuffled = [e["question_id"] for e in dataset.select_slice(list(reversed(entries)), 10, seed=7)]
    other = [e["question_id"] for e in dataset.select_slice(entries, 10, seed=8)]
    assert first == again == shuffled
    assert first != other
    assert len(set(first)) == 10


def test_slice_size_is_bounded():
    with pytest.raises(ValueError, match="slice must be between 1 and 40"):
        dataset.select_slice(fake_dataset(), 41, seed=0)
    with pytest.raises(ValueError):
        dataset.select_slice(fake_dataset(), 0, seed=0)


def test_dataset_hash_mismatch_is_refused(tmp_path):
    path = tmp_path / "longmemeval_s_cleaned.json"
    path.write_text(json.dumps(fake_dataset()), encoding="utf-8")
    with pytest.raises(dataset.DatasetHashMismatch, match="not the pinned dataset"):
        dataset.load(path)
    assert dataset.load(path, dataset.sha256_of(path)) == fake_dataset()


def test_cli_refuses_a_file_that_is_not_the_pinned_dataset(tmp_path):
    path = tmp_path / "other.json"
    path.write_text("[]", encoding="utf-8")
    result = CliRunner().invoke(main, ["run", "--adapter", "bm25", "--data", str(path), "--out", str(tmp_path)])
    assert result.exit_code == 2
    assert "Refusing to score" in result.output


# ---- report: every setting is visible ----


def test_report_contains_every_setting(fixture_entries):
    report = run(fixture_entries, "bm25", k=5, seed=3)
    text = render_markdown(report)
    for key in SETTING_ORDER:
        assert f"| {key} | {report['settings'][key]} |" in text
    assert "recall_any@5" in text and "95% Wilson interval" in text
    assert "No LLM was involved" in text


def test_report_labels_the_local_judge_as_weaker(fixture_entries):
    report = run(fixture_entries, "bm25", judge=lambda q, a, ctx: True, judge_label="ollama:tiny")
    text = render_markdown(report)
    assert report["answer_level"]["hits"] == 5
    assert "weaker than the GPT-4o judge" in text


# ---- compare: refusal when settings differ ----


@pytest.fixture
def claims_doc():
    return load_claims(CLAIMS_FILE)


def make_report(**overrides):
    settings = {
        "adapter": "mempalace-raw", "library": "mempalace", "library_version": "mempalace 3.11.0",
        "pipeline": "vector_only", "dataset": "longmemeval_s_cleaned", "metric": "recall_any", "k": 5,
        "index_text": "user_only", "granularity": "session", "judge": "none", "slice_size": 50, "seed": 0,
    }
    settings.update(overrides)
    cell = {"hits": 47, "n": 50, "rate": 0.94, "ci_low": 0.838, "ci_high": 0.979}
    return {"settings": settings, "adapter_errors": [], "recall_any": {"5": cell, "10": cell}}


def raw_only(doc):
    doc = copy.deepcopy(doc)
    doc["claims"] = [c for c in doc["claims"] if c["id"] == "raw_recall_at_5"]
    return doc


def test_matching_settings_print_measured_next_to_claimed(claims_doc):
    text = compare(raw_only(claims_doc), make_report())
    assert "Claimed value: 96.6% on 500 questions" in text
    assert "Measured 94.0% (47/50" in text
    assert "inside the measured interval" in text
    assert "NOT COMPARED" not in text
    assert "line 7, 241-249" in text


def test_differing_settings_refuse_and_name_the_setting(claims_doc):
    text = compare(raw_only(claims_doc), make_report(pipeline="library_default", index_text="all_turns"))
    assert "NOT COMPARED" in text
    assert "pipeline (claimed vector_only, run library_default)" in text
    assert "index_text (claimed user_only, run all_turns)" in text
    assert "Measured" not in text and "inside" not in text and "outside" not in text


def test_judge_mismatch_refuses(claims_doc):
    text = compare(raw_only(claims_doc), make_report(judge="ollama:qwen2.5:3b-instruct"))
    assert "judge (claimed none, run ollama:qwen2.5:3b-instruct)" in text


def test_outside_interval_is_stated_without_judgement_words(claims_doc):
    report = make_report()
    report["recall_any"]["5"].update(rate=0.80, ci_low=0.67, ci_high=0.89, hits=40)
    text = compare(raw_only(claims_doc), report)
    assert "outside the measured interval" in text
    for word in ("fraud", "lying", "false", "misleading"):
        assert word not in text.lower()


def test_adapter_errors_block_attribution(claims_doc):
    report = make_report()
    report["adapter_errors"] = [{"question_id": "q1", "error": "boom"}]
    assert "cannot be attributed to the library" in compare(raw_only(claims_doc), report)


def test_wrong_library_is_refused(claims_doc):
    text = compare(claims_doc, make_report(library="bm25", adapter="bm25"))
    assert "claim file is for mempalace" in text and "Measured" not in text


def test_baseline_is_shown_beside_the_claim(claims_doc):
    baseline = make_report(adapter="bm25", library="bm25", pipeline="bm25", library_version="n/a")
    text = compare(raw_only(claims_doc), make_report(), [baseline])
    assert "Baseline bm25" in text and "recall_any@5 94.0%" in text


def test_shipped_claim_file_cites_the_readme_and_unsupported_pipeline_is_refused(claims_doc):
    assert all("README.md" == claims_doc["source"]["file"] for _ in claims_doc["claims"])
    text = compare(claims_doc, make_report())
    assert "hybrid_v4_heldout_recall_at_5" in text
    assert "pipeline (claimed hybrid_v4, run vector_only)" in text


def test_claim_without_settings_is_rejected(tmp_path):
    bad = tmp_path / "bad.yaml"
    bad.write_text(
        yaml.safe_dump({
            "library": "x", "source": {"file": "R", "line": 1, "url": "u"},
            "claims": [{"id": "c", "quote": "q", "value": 0.9, "settings": {"k": 5}}],
        })
    )
    with pytest.raises(ClaimFileError, match="does not state"):
        load_claims(bad)


# ---- judge parsing ----


def test_verdict_parsing_is_conservative():
    assert parse_verdict(" Yes, it matches") is True
    assert parse_verdict("No") is False
    assert parse_verdict("I think so, yes") is False


def test_ollama_judge_uses_reader_then_judge_prompt():
    prompts = []

    def fake_generate(model, prompt):
        prompts.append(prompt)
        return "Biscuit" if len(prompts) == 1 else "yes"

    judge = ollama_judge("tiny", generate=fake_generate)
    assert judge("What is the dog called?", "Biscuit", ["My dog is Biscuit"]) is True
    assert "My dog is Biscuit" in prompts[0] and "Reference answer: Biscuit" in prompts[1]

import pytest

from claimledger import adapters
from claimledger.adapters.base import Adapter


def make_entry(qid, question, answer_ids, sessions, qtype="single-session-user"):
    """sessions: {session_id: user text}"""
    return {
        "question_id": qid,
        "question_type": qtype,
        "question": question,
        "answer": "x",
        "answer_session_ids": answer_ids,
        "haystack_session_ids": list(sessions),
        "haystack_dates": ["2026/01/01"] * len(sessions),
        "haystack_sessions": [
            [{"role": "user", "content": text}, {"role": "assistant", "content": "ok"}]
            for text in sessions.values()
        ],
    }


@pytest.fixture
def fixture_entries():
    """Five questions whose evidence session is lexically unambiguous."""
    topics = [
        ("q1", "which cheese did I buy", "s_cheese", "I bought a wheel of gruyere cheese at the market"),
        ("q2", "what is my dog called", "s_dog", "My dog is called Biscuit and she loves swimming"),
        ("q3", "which museum did we visit", "s_museum", "We visited the maritime museum in Rotterdam"),
        ("q4", "what instrument do I practise", "s_cello", "I practise the cello every evening"),
        ("q5", "which marathon am I training for", "s_marathon", "I am training for the Berlin marathon"),
    ]
    noise = {f"n{i}": f"filler talk about weather number {i} and nothing else" for i in range(6)}
    return [
        make_entry(qid, question, [sid], {**noise, sid: text}) for qid, question, sid, text in topics
    ]


class BrokenAdapter(Adapter):
    """Ranks the worst session first: must fail the selftest, never be scored."""

    name = "broken"
    library = "broken"
    pipeline = "broken"

    def ingest(self, documents):
        self._ids = [sid for sid, _ in documents]

    def search(self, query, k):
        return list(reversed(self._ids))[:k]


@pytest.fixture
def register_broken(monkeypatch):
    original = adapters.make

    def make(name):
        return BrokenAdapter() if name == "broken" else original(name)

    monkeypatch.setattr(adapters, "make", make)
    monkeypatch.setattr("claimledger.runner.make", make)

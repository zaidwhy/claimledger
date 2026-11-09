import math
import re
from collections import Counter

from .base import Adapter

_TOKEN = re.compile(r"\w+")


class Bm25Adapter(Adapter):
    """Plain Okapi BM25 over one document per session. The floor every library must clear."""

    name = "bm25"
    library = "bm25"
    pipeline = "bm25"

    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1, self.b = k1, b
        self._ids: list[str] = []
        self._counts: list[Counter] = []
        self._lengths: list[int] = []
        self._doc_freq: Counter = Counter()

    def ingest(self, documents):
        for session_id, text in documents:
            tokens = _TOKEN.findall(text.lower())
            counts = Counter(tokens)
            self._ids.append(session_id)
            self._counts.append(counts)
            self._lengths.append(len(tokens))
            self._doc_freq.update(counts.keys())

    def search(self, query, k):
        n = len(self._ids)
        if n == 0:
            return []
        average = sum(self._lengths) / n or 1.0
        terms = set(_TOKEN.findall(query.lower()))
        scores = []
        for index, counts in enumerate(self._counts):
            score = 0.0
            for term in terms:
                frequency = counts.get(term, 0)
                if not frequency:
                    continue
                idf = math.log(1 + (n - self._doc_freq[term] + 0.5) / (self._doc_freq[term] + 0.5))
                norm = frequency + self.k1 * (1 - self.b + self.b * self._lengths[index] / average)
                score += idf * frequency * (self.k1 + 1) / norm
            scores.append((-score, index))
        scores.sort()
        return [self._ids[index] for _, index in scores[:k]]

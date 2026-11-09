import shutil
import tempfile

from .base import Adapter

WING, ROOM = "longmemeval", "sessions"


class MempalaceAdapter(Adapter):
    """Drives the installed mempalace package.

    Ingest: one drawer per session, written through the library's own collection
    (verbatim text, no chunking, no closets, no AAAK). The palace is built fresh
    per question, as the README's benchmark does.

    raw=True queries the drawers collection directly (vector search only), which is
    the pipeline the README labels "Raw (semantic search, no heuristics, no LLM)".
    raw=False calls mempalace.searcher.search_memories with defaults, the path a user's
    agent actually takes, which adds lexical and closet ranking.
    """

    library = "mempalace"

    def __init__(self, raw: bool):
        self.raw = raw
        self.name = "mempalace-raw" if raw else "mempalace"
        self.pipeline = "vector_only" if raw else "library_default"
        self._dir = tempfile.mkdtemp(prefix="claimledger_palace_")
        self._collection = None
        self._count = 0

    def library_version(self):
        from importlib.metadata import version

        return f"mempalace {version('mempalace')}"

    def ingest(self, documents):
        from mempalace.palace import get_collection

        self._collection = get_collection(self._dir)
        self._count = len(documents)
        if not documents:
            return
        self._collection.upsert(
            documents=[text for _, text in documents],
            ids=[f"session_{index}" for index in range(len(documents))],
            metadatas=[
                {"wing": WING, "room": ROOM, "source_file": session_id, "chunk_index": 0}
                for session_id, _ in documents
            ],
        )

    def search(self, query, k):
        if not self._count:
            return []
        if self.raw:
            found = self._collection.query(
                query_texts=[query], n_results=min(k, self._count), include=["metadatas"]
            )
            return [meta["source_file"] for meta in found["metadatas"][0]]
        found = _search_memories(query, self._dir, n_results=k)
        return [hit["source_file"] for hit in found.get("results", [])]

    def close(self):
        self._collection = None
        shutil.rmtree(self._dir, ignore_errors=True)


def _search_memories(query, palace_path, n_results):
    from mempalace.searcher import search_memories

    return search_memories(query, palace_path, n_results=n_results)

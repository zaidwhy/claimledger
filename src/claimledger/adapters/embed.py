import itertools

from .base import Adapter

_collection_counter = itertools.count()


class EmbedAdapter(Adapter):
    """Plain dense retrieval: ChromaDB's default embedding model, cosine nearest neighbours,
    one document per session, nothing else. This is the floor for any library built on Chroma."""

    name = "embed"
    library = "chromadb"
    pipeline = "vector_only"

    def __init__(self):
        import chromadb

        self._client = chromadb.EphemeralClient()
        self._collection = self._client.create_collection(
            f"claimledger_{next(_collection_counter)}", metadata={"hnsw:space": "cosine"}
        )
        self._ids: list[str] = []

    def library_version(self):
        import chromadb

        return f"chromadb {chromadb.__version__} default embedding"

    def ingest(self, documents):
        self._ids = [session_id for session_id, _ in documents]
        self._collection.add(
            documents=[text for _, text in documents],
            ids=[f"doc_{i}" for i in range(len(documents))],
        )

    def search(self, query, k):
        if not self._ids:
            return []
        found = self._collection.query(query_texts=[query], n_results=min(k, len(self._ids)))
        return [self._ids[int(doc_id.split("_", 1)[1])] for doc_id in found["ids"][0]]

    def close(self):
        self._client.delete_collection(self._collection.name)

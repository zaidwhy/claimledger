class Adapter:
    """What every adapter must do: take (session_id, text) pairs, answer queries with session ids.

    The runner builds the text, so every adapter sees byte-identical input.
    """

    name = "base"
    library = "base"
    pipeline = "unspecified"

    def library_version(self) -> str:
        return "n/a"

    def ingest(self, documents: list[tuple[str, str]]) -> None:
        raise NotImplementedError

    def search(self, query: str, k: int) -> list[str]:
        """Session ids, best first. May repeat ids (chunks); the runner dedupes."""
        raise NotImplementedError

    def close(self) -> None:
        pass

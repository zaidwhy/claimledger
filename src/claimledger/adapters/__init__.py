from .base import Adapter
from .bm25 import Bm25Adapter


def make(name: str) -> Adapter:
    """Heavy dependencies are imported only for the adapter that needs them."""
    if name == "bm25":
        return Bm25Adapter()
    if name == "embed":
        from .embed import EmbedAdapter

        return EmbedAdapter()
    if name in ("mempalace", "mempalace-raw"):
        from .mempalace import MempalaceAdapter

        return MempalaceAdapter(raw=name == "mempalace-raw")
    raise ValueError(f"unknown adapter {name!r}; choose from {', '.join(ADAPTER_NAMES)}")


ADAPTER_NAMES = ("bm25", "embed", "mempalace-raw", "mempalace")

"""LongMemEval loading, integrity check and seeded slicing."""
import hashlib
import json
import random
import urllib.request
from pathlib import Path

DATASET_NAME = "longmemeval_s_cleaned"
DATASET_URL = (
    "https://huggingface.co/datasets/xiaowu0162/longmemeval-cleaned/"
    "resolve/main/longmemeval_s_cleaned.json"
)
# Recorded 2026-11-09 from the file served at DATASET_URL (277,383,467 bytes, 500 questions).
DATASET_SHA256 = "d6f21ea9d60a0d56f34a05b609c79c88a451d2ae03597821ea3d5a9678c3a442"
MAX_SLICE = 500


class DatasetHashMismatch(Exception):
    pass


def sha256_of(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def fetch(dest: Path) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(DATASET_URL, timeout=60) as response, open(dest, "wb") as out:
        while block := response.read(1 << 20):
            out.write(block)
    verify(dest, DATASET_SHA256)
    return dest


def verify(path: Path, expected_sha256: str) -> str:
    actual = sha256_of(path)
    if actual != expected_sha256:
        raise DatasetHashMismatch(
            f"{path} has sha256 {actual}, expected {expected_sha256}. "
            "Refusing to score a file that is not the pinned dataset."
        )
    return actual


def load(path: Path, expected_sha256: str = DATASET_SHA256) -> list[dict]:
    verify(path, expected_sha256)
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def select_slice(entries: list[dict], size: int, seed: int) -> list[dict]:
    """Seeded sample over question ids sorted first, so file order never matters."""
    if not 1 <= size <= min(MAX_SLICE, len(entries)):
        raise ValueError(f"slice must be between 1 and {min(MAX_SLICE, len(entries))}, got {size}")
    by_id = {entry["question_id"]: entry for entry in entries}
    chosen = random.Random(seed).sample(sorted(by_id), size)
    return [by_id[question_id] for question_id in chosen]

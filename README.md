# claimledger

A memory library's README says "96.6% R@5 on LongMemEval". Which questions, which k, which index text, which retrieval path, which judge, and what does plain BM25 score on the same questions? claimledger runs the library on a fixed, seeded slice of LongMemEval and prints what it measured next to what was claimed, with every setting on both sides. When the settings differ, it says which setting differs and states no gap.

It reports numbers and settings. It does not classify a claim as anything.

**First result (2026-11-10).** mempalace 3.11.0's "96.6% R@5 raw on LongMemEval" reproduces exactly: 483 of 500 with every setting matched. Plain BM25 on the same 500 questions scores 95.2% (476 of 500). 19 questions are found only by mempalace and 12 only by BM25 (exact McNemar p = 0.28), so recall at k=5 on this benchmark does not separate the two. Full table and the other values of k are under [Measurements](#measurements-2026-11-09-and-2026-11-10-local-cpu).

## The two failure modes it is built around

1. **Comparing apples to oranges.** A number measured at k=10, or with assistant turns indexed, or through a different retrieval path, is not a reproduction of a number claimed at k=5. `compare` checks library, pipeline, dataset, metric, k, index_text, granularity and judge. Any difference prints `NOT COMPARED` with the differing settings, and no measured-versus-claimed sentence is produced.
2. **A flaky adapter blamed on the library.** Every adapter is a short file. Before a run it must pass a three-session fixture (`claimledger selftest`); a run with any per-question adapter error is excluded from comparison. Two baselines (plain BM25, plain ChromaDB embedding retrieval) run over the same slice, so the floor is on the page next to the library.

## Two scores, kept apart

- **Retrieval-only (the headline).** Did an evidence session come back in the top k. `recall_any` is the proportion of questions with at least one evidence session in the top k; `recall_all` needs every evidence session. No LLM is involved. Reported with a 95% Wilson interval and the sample size.
- **Answer-level (optional, secondary).** `--judge-model qwen2.5:3b-instruct` has a local Ollama model read the top-k sessions, answer, and then judge its own answer against the gold answer. This judge is weaker than the GPT-4o judge used in the LongMemEval paper, so the number is labelled as such in the report and is never compared against a claim that names a different judge.

## Install and run

```
pip install -e ".[embed]"            # baselines
pip install -e ".[mempalace]"        # also installs mempalace 3.11.0 from PyPI
claimledger fetch                    # LongMemEval-S cleaned, 277 MB, sha256 verified
claimledger run --adapter bm25 --slice 50 --seed 0
claimledger run --adapter embed --slice 50 --seed 0
claimledger run --adapter mempalace-raw --slice 50 --seed 0
claimledger compare --claims claims/mempalace.yaml \
    --report results/mempalace-raw_n50_seed0_k5.json \
    --baseline results/bm25_n50_seed0_k5.json --baseline results/embed_n50_seed0_k5.json
```

Reports (markdown and JSON) go to `results/`, which is gitignored except for the seed-0 reports this README cites, committed so every number below traces to a file. Other reports about a named project stay local until the person who ran them decides what to do with them.

## Measurements (2026-11-09 and 2026-11-10, local, CPU)

recall_any@5, user-turn session documents, seed 0. The 500-question rows cover every question in LongMemEval-S, the sample size of the README claim.

| adapter | pipeline | questions | recall_any@5 | 95% interval |
|---|---|---|---|---|
| bm25 | bm25 | 50 | 96.0% (48/50) | 86.5% to 98.9% |
| bm25 | bm25 | 500 | 95.2% (476/500) | 93.0% to 96.8% |
| embed | vector_only | 50 | 100.0% (50/50) | 92.9% to 100.0% |
| mempalace-raw 3.11.0 | vector_only | 50 | 100.0% (50/50) | 92.9% to 100.0% |
| mempalace-raw 3.11.0 | vector_only | 500 | 96.6% (483/500) | 94.6% to 97.9% |
| mempalace 3.11.0 (search_memories defaults) | library_default | 50 | 100.0% (50/50) | 92.9% to 100.0% |

The raw-retrieval claim reproduces: `mempalace-raw` measured 96.6% (483/500), the README's own number, with every setting matched (`claimledger compare --claims claims/mempalace.yaml --report results/mempalace-raw_n500_seed0_k5.json --baseline results/bm25_n500_seed0_k5.json`). The same run shows what the number does not say: plain BM25 on the same 500 questions reaches 95.2% (476/500), and the two intervals overlap, so this benchmark at k=5 cannot separate the library's vector retrieval from keyword search. Question by question, 19 questions hit at k=5 only with mempalace-raw and 12 only with BM25 (exact McNemar p = 0.28, from the `per_question` rows of the two committed 500-question reports). BM25 is ahead at k=1 (82.6% against 80.6%) and k=3 (93.2% against 92.6%); vector retrieval is ahead at k=10 (98.2% against 97.0%) and on recall_all@5 (85.0% against 81.0%), where every evidence session must be retrieved. An earlier 500-question attempt aborted with `memory allocation of 425984 bytes failed` while the disk had 358 MB free; the rerun with about 10 GB free finished in 793 s with 0 adapter errors, so the abort was the machine, not the library. The `mempalace` adapter's pipeline label (`library_default`) differs from the claim's (`vector_only`), so `compare` refuses it.

## Data

`longmemeval_s_cleaned.json` from `xiaowu0162/longmemeval-cleaned` on Hugging Face (500 questions, about 48 sessions each). The pinned sha256 is `d6f21ea9d60a0d56f34a05b609c79c88a451d2ae03597821ea3d5a9678c3a442`, recorded 2026-11-09. A file with any other hash is refused. The slice is `random.Random(seed).sample` over question ids sorted first, so file order cannot change it. The oracle split is not used: it contains only evidence sessions, so retrieval there is trivial.

## Adapters

| adapter | what it does | pipeline label |
|---|---|---|
| `bm25` | Okapi BM25 (k1 1.5, b 0.75), one document per session | `bm25` |
| `embed` | ChromaDB default embedding (all-MiniLM-L6-v2), cosine, one document per session | `vector_only` |
| `mempalace-raw` | mempalace 3.11.0 drawers collection, one drawer per session, vector query only | `vector_only` |
| `mempalace` | same palace through `mempalace.searcher.search_memories` defaults (lexical and closet ranking added) | `library_default` |

The runner builds each session's text (`--index-text user_only`, the default, joins user turns; `all_turns` includes the assistant) so every adapter sees identical input. mempalace's README benchmark indexes user turns only, which is why that is the default. A question whose evidence sits in assistant text (`single-session-assistant`) is disadvantaged under `user_only`; the per-type table shows it.

What was tried for the real library: `pip install mempalace` installs cleanly (3.11.0, depends on chromadb, numpy, onnxruntime, pyyaml). mem0 was not needed.

## Claim files

`claims/mempalace.yaml` records each claim with the README line, a quote, the value, and the settings the README gives for it. A claim that omits a setting is rejected at load, because it cannot be compared. Claims whose pipeline no adapter implements (for example the README's "hybrid v4") are listed and refused with the reason.

## Limits

- A 50-question slice has a wide interval; read the interval, not the point value. `--slice 500` is the full benchmark.
- Only `recall_any@k` claims at session granularity are comparable today.
- The README claims are matched to settings by reading the README and the benchmark script. Where the README does not state a setting, the claim file says so in its `note`.
- ChromaDB's default embedding on CPU is slow; a 50-question slice takes several minutes.

## Tests

`pytest` (28 tests): recall against a hand-made fixture with known answers, deterministic slicing, dataset hash refusal, every setting present in the report, refusal text for each mismatched setting, claim files without settings rejected, judge parsing.

# claimledger report: bm25

Retrieval-only recall_any@5: **95.2%** (476/500, 95% Wilson interval 93.0% to 96.8%). No LLM was involved in this number.

## Settings

| setting | value |
|---|---|
| adapter | bm25 |
| library | bm25 |
| library_version | n/a |
| pipeline | bm25 |
| dataset | longmemeval_s_cleaned |
| dataset_sha256 | d6f21ea9d60a0d56f34a05b609c79c88a451d2ae03597821ea3d5a9678c3a442 |
| metric | recall_any |
| k | 5 |
| index_text | user_only |
| granularity | session |
| judge | none |
| slice_size | 500 |
| seed | 0 |
| claimledger_version | 0.1.0 |

Questions scored: 500 of 500 in the slice. Adapter errors: 0.

## Retrieval recall (session level)

| metric | rate | hits | 95% interval |
|---|---|---|---|
| recall_any@1 | 82.6% | 413/500 | 79.0% to 85.7% |
| recall_any@3 | 93.2% | 466/500 | 90.6% to 95.1% |
| recall_any@5 | 95.2% | 476/500 | 93.0% to 96.8% |
| recall_any@10 | 97.0% | 485/500 | 95.1% to 98.2% |
| recall_all@1 | 26.8% | 134/500 | 23.1% to 30.8% |
| recall_all@3 | 75.4% | 377/500 | 71.4% to 79.0% |
| recall_all@5 | 81.0% | 405/500 | 77.3% to 84.2% |
| recall_all@10 | 88.4% | 442/500 | 85.3% to 90.9% |

## recall_any@5 by question type

| type | rate | hits | 95% interval |
|---|---|---|---|
| knowledge-update | 100.0% | 78/78 | 95.3% to 100.0% |
| multi-session | 96.2% | 128/133 | 91.5% to 98.4% |
| single-session-assistant | 92.9% | 52/56 | 83.0% to 97.2% |
| single-session-preference | 73.3% | 22/30 | 55.6% to 85.8% |
| single-session-user | 98.6% | 69/70 | 92.3% to 99.7% |
| temporal-reasoning | 95.5% | 127/133 | 90.5% to 97.9% |

Small cells have wide intervals; read the interval, not the point value.

Run time: 2.9 s.

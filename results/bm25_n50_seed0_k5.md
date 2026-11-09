# claimledger report: bm25

Retrieval-only recall_any@5: **96.0%** (48/50, 95% Wilson interval 86.5% to 98.9%). No LLM was involved in this number.

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
| slice_size | 50 |
| seed | 0 |
| claimledger_version | 0.1.0 |

Questions scored: 50 of 50 in the slice. Adapter errors: 0.

## Retrieval recall (session level)

| metric | rate | hits | 95% interval |
|---|---|---|---|
| recall_any@1 | 78.0% | 39/50 | 64.8% to 87.2% |
| recall_any@3 | 90.0% | 45/50 | 78.6% to 95.7% |
| recall_any@5 | 96.0% | 48/50 | 86.5% to 98.9% |
| recall_any@10 | 100.0% | 50/50 | 92.9% to 100.0% |
| recall_all@1 | 18.0% | 9/50 | 9.8% to 30.8% |
| recall_all@3 | 64.0% | 32/50 | 50.1% to 75.9% |
| recall_all@5 | 74.0% | 37/50 | 60.4% to 84.1% |
| recall_all@10 | 84.0% | 42/50 | 71.5% to 91.7% |

## recall_any@5 by question type

| type | rate | hits | 95% interval |
|---|---|---|---|
| knowledge-update | 100.0% | 7/7 | 64.6% to 100.0% |
| multi-session | 94.4% | 17/18 | 74.2% to 99.0% |
| single-session-assistant | 50.0% | 1/2 | 9.5% to 90.5% |
| single-session-preference | 100.0% | 1/1 | 20.7% to 100.0% |
| single-session-user | 100.0% | 8/8 | 67.6% to 100.0% |
| temporal-reasoning | 100.0% | 14/14 | 78.5% to 100.0% |

Small cells have wide intervals; read the interval, not the point value.

Run time: 0.4 s.

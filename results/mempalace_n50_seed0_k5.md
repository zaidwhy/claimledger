# claimledger report: mempalace

Retrieval-only recall_any@5: **100.0%** (50/50, 95% Wilson interval 92.9% to 100.0%). No LLM was involved in this number.

## Settings

| setting | value |
|---|---|
| adapter | mempalace |
| library | mempalace |
| library_version | mempalace 3.11.0 |
| pipeline | library_default |
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
| recall_any@1 | 86.0% | 43/50 | 73.8% to 93.0% |
| recall_any@3 | 98.0% | 49/50 | 89.5% to 99.6% |
| recall_any@5 | 100.0% | 50/50 | 92.9% to 100.0% |
| recall_any@10 | 100.0% | 50/50 | 92.9% to 100.0% |
| recall_all@1 | 22.0% | 11/50 | 12.8% to 35.2% |
| recall_all@3 | 76.0% | 38/50 | 62.6% to 85.7% |
| recall_all@5 | 84.0% | 42/50 | 71.5% to 91.7% |
| recall_all@10 | 94.0% | 47/50 | 83.8% to 97.9% |

## recall_any@5 by question type

| type | rate | hits | 95% interval |
|---|---|---|---|
| knowledge-update | 100.0% | 7/7 | 64.6% to 100.0% |
| multi-session | 100.0% | 18/18 | 82.4% to 100.0% |
| single-session-assistant | 100.0% | 2/2 | 34.2% to 100.0% |
| single-session-preference | 100.0% | 1/1 | 20.7% to 100.0% |
| single-session-user | 100.0% | 8/8 | 67.6% to 100.0% |
| temporal-reasoning | 100.0% | 14/14 | 78.5% to 100.0% |

Small cells have wide intervals; read the interval, not the point value.

Run time: 94.5 s.

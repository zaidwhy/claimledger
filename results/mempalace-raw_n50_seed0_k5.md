# claimledger report: mempalace-raw

Retrieval-only recall_any@5: **100.0%** (50/50, 95% Wilson interval 92.9% to 100.0%). No LLM was involved in this number.

## Settings

| setting | value |
|---|---|
| adapter | mempalace-raw |
| library | mempalace |
| library_version | mempalace 3.11.0 |
| pipeline | vector_only |
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
| recall_any@1 | 80.0% | 40/50 | 67.0% to 88.8% |
| recall_any@3 | 92.0% | 46/50 | 81.2% to 96.8% |
| recall_any@5 | 100.0% | 50/50 | 92.9% to 100.0% |
| recall_any@10 | 100.0% | 50/50 | 92.9% to 100.0% |
| recall_all@1 | 20.0% | 10/50 | 11.2% to 33.0% |
| recall_all@3 | 68.0% | 34/50 | 54.2% to 79.2% |
| recall_all@5 | 78.0% | 39/50 | 64.8% to 87.2% |
| recall_all@10 | 90.0% | 45/50 | 78.6% to 95.7% |

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

Run time: 65.1 s.

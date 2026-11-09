# claimledger report: mempalace-raw

Retrieval-only recall_any@5: **96.6%** (483/500, 95% Wilson interval 94.6% to 97.9%). No LLM was involved in this number.

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
| slice_size | 500 |
| seed | 0 |
| claimledger_version | 0.1.0 |

Questions scored: 500 of 500 in the slice. Adapter errors: 0.

## Retrieval recall (session level)

| metric | rate | hits | 95% interval |
|---|---|---|---|
| recall_any@1 | 80.6% | 403/500 | 76.9% to 83.8% |
| recall_any@3 | 92.6% | 463/500 | 90.0% to 94.6% |
| recall_any@5 | 96.6% | 483/500 | 94.6% to 97.9% |
| recall_any@10 | 98.2% | 491/500 | 96.6% to 99.1% |
| recall_all@1 | 27.0% | 135/500 | 23.3% to 31.1% |
| recall_all@3 | 73.4% | 367/500 | 69.4% to 77.1% |
| recall_all@5 | 85.0% | 425/500 | 81.6% to 87.9% |
| recall_all@10 | 93.2% | 466/500 | 90.6% to 95.1% |

## recall_any@5 by question type

| type | rate | hits | 95% interval |
|---|---|---|---|
| knowledge-update | 100.0% | 78/78 | 95.3% to 100.0% |
| multi-session | 99.2% | 132/133 | 95.9% to 99.9% |
| single-session-assistant | 96.4% | 54/56 | 87.9% to 99.0% |
| single-session-preference | 96.7% | 29/30 | 83.3% to 99.4% |
| single-session-user | 91.4% | 64/70 | 82.5% to 96.0% |
| temporal-reasoning | 94.7% | 126/133 | 89.5% to 97.4% |

Small cells have wide intervals; read the interval, not the point value.

Run time: 792.9 s.

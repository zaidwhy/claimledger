# claimledger v2: paper plan (started 2026-11-20)

Target: TMLR (rolling, double blind, no novelty requirement; reproducibility studies are in scope and can earn the
Reproducibility Certification). Working title: "Which memory benchmark numbers have a file behind them? Vendor
claims on LongMemEval and LoCoMo, recounted and re-run under one setup."

## Thesis

A memory vendor's headline number is a claim about one run of one stack under one answerer and judge. The paper asks
three questions per claim, cheapest first, and stops at the first one that cannot be answered:

1. **Artifact.** Is there a per-question file for the run behind the headline, and does it recount to the headline?
2. **Judge.** Holding the vendor's own generated answers fixed, how far does the score move under a second judge and
   under the LongMemEval paper's question-type prompts?
3. **Matched rerun.** Under one fixed answerer, judge, dataset hash and top-k, what do the open-source stacks score,
   next to plain BM25 and embedding baselines on the same questions?

The opinion that makes it not a leaderboard: a number with no file behind it is reported as "no artifact", not as a
score, and no claim is called reproduced or refuted when any setting differs (`compare` prints NOT COMPARED).

## Status of each claim (verified 2026-11-20 unless marked)

| Vendor | Headline | Arm 1 (artifact) | Arm 2 (judge) | Arm 3 (rerun) |
|---|---|---|---|---|
| MemPalace 3.11.0 | 96.6% R@5, LongMemEval-S | reproduces exactly, 483/500; BM25 476/500, McNemar p = 0.28 (done 2026-11-10) | n/a (retrieval only) | done |
| Mem0 Platform | LME 94.4 / 94.8, LoCoMo 92.5 / 91.8 (top 200 / 50) | **no file for any of the four.** Committed files (edcd6f1, gpt-5 answerer and judge) recount to 467/500, 452/500, 1410/1540, 1273/1540, the README's values before PR #8 (2026-05-13) raised them and changed only README.md | possible on the April files ($, answers are in the files) | platform: terms 2.3(i) restrict benchmarking, not run; OSS SDK: Apache 2.0, runnable |
| Zep Cloud | LoCoMo 94.7, LME 90.2 (gpt-5.4) | no file on the claims page; committed `benchmarks/locomo/experiments` are 5 configs x 10 runs with gpt-4o-mini, means 0.696 to 0.803, a different setting | only on committed LoCoMo runs | Cloud: terms 2.3(i) need written consent to publish; Graphiti (Apache 2.0) runnable |
| Zep paper 2025 | LME-S 71.2 (gpt-4o) | not yet checked | | Graphiti + gpt-4o-mini extraction |
| Supermemory | "#1", 95% Recall@15 / 97% Recall@20 on LME | not yet checked; its own compare page says "Neither has been reproduced under a matched setup" (supermemory.ai/compare/supermemory-vs-mem0, quote from a fetch agent, re-read before citing) | | retrieval claim fits Arm 3 at $0 if self-host runs |
| Letta | LoCoMo 74.0 (gpt-4o-mini, filesystem agent) | blog names no judge and no harness | | not reproducible as stated |

## Prior work (from a search agent, 2026-11-20; open each before citing)

- Maximem, "The state of AI memory in 2026: claimed vs observed" (blog, 2026-05-27): re-ran Mem0 and Zep with gpt-5; a
  competitor, no per-question file diff. Partial overlap; must be cited.
- arXiv 2609.38021 (repeated judging, reader variation, negative controls on LongMemEval-S, one custom chain): overlaps Arm 2.
- arXiv 2609.22231 EvalMem (seven memory systems, LoCoMo + LME-S, EMNLP 2026 Findings): full text not read; could pre-empt
  Arm 3. **Read before spending money.**
- arXiv 2604.21284 (MemPalace critical analysis), Penfield Labs LoCoMo key audit, getzep/zep-papers#5, mem0#7641.
- No found work diffs vendor headlines against vendor per-question files. That is Arm 1 and the paper's lead.

## Order of work

1. Read EvalMem and Maximem in full; write the related-work paragraph -> verify: overlap stated per arm.
2. Arm 1 for Zep 2025 paper, Supermemory, Letta -> verify: each row has a pinned URL + commit or "no artifact".
3. Arm 2 on Mem0's April files: re-judge the committed generated answers with gpt-4o and the LongMemEval prompts, and with
   one open judge -> verify: per-question agreement table, kappa, and the score under each judge. Needs a key.
4. Arm 3: mem0 OSS, Graphiti, Supermemory self-host, MemPalace, BM25, embed on LongMemEval-S (pinned sha256), one answerer
   and judge, 3 repeats -> verify: claimledger reports with every setting, McNemar against BM25. Needs a key and budget;
   run one conversation first to measure real cost.
5. Write-up in the TMLR template, anonymized; supplement = this repo at a tag.

## Decisions that are Zaid's

- API budget and key (Arms 2 and 3). The $120 to $650 range in the opportunity note is not checked; the first smoke run
  measures it.
- Whether to write to Mem0 asking for the files behind the PR #8 numbers before submission. Asking is fair practice and
  makes Arm 1 stronger; Zaid writes it.
- Platform runs (Mem0, Zep Cloud): skip, or ask for written consent.
- Timing against exams, and when anything about a named vendor goes public (TMLR is double blind; a public repo under his
  name with these findings is a de-anonymization question to settle first).

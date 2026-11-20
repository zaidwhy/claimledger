# claimledger handoff (2026-11-10)

State: main pushed to private zaidwhy/claimledger (remote created by Zaid 2026-11-10). 28 tests pass. data/ is gitignored; results/ commits only the seed-0 reports the README cites.

Finding: MemPalace's "96.6% R@5 raw" reproduces exactly (483/500, all settings matched). Plain BM25 gets 95.2% (476/500) on the same questions; 19 vs 12 discordant questions, exact McNemar p = 0.28, so k=5 recall on LongMemEval-S does not separate the two. BM25 leads at k=1 and k=3.

Next (Zaid's call, outward-facing): decide whether anything goes on MemPalace#27. Nothing has been posted.

2026-11-10 afternoon: Zaid said to launch. Headline numbers recomputed from the two committed 500-question reports (483 vs 476, 19 vs 12 discordant, p = 0.281; k=1 403 vs 413, k=3 463 vs 466, k=10 491 vs 485) and the README now states the result under the thesis. Checked live: MemPalace README still claims 96.6%, #27 open with 234 thumbs-up and 39 comments, none mentioning BM25. Zaid made the repo PUBLIC the same day and asked for the #27 comment to be written and posted this once: https://github.com/MemPalace/mempalace/issues/27#issuecomment-6765865311 . Next: watch the thread; Zaid writes any replies.

## Overnight decisions (review)
- No per-question process isolation added. The earlier 500-run crash happened at 358 MB free disk; the rerun at about 10 GB free finished with 0 errors, so the fix was disk space, not code.
- Committed the 6 seed-0 reports the README cites (results/*_n50_* and *_n500_*, about 0.6 MB) so its numbers trace to files; the repo is private, so nothing is published. Other results stay ignored.

## 2026-11-20 evening: v2 paper started (branch d280-claims, 3 local commits, NOT pushed)

Plan, findings and decisions: `PAPER-PLAN.md`. Target TMLR. Zaid's rule: $0 only, skip anything that needs paid API calls.

- New `claimledger tally <file>` recounts a vendor per-question file (mem0 memory-benchmarks format). 32 tests pass (`.venv`, created this session; `pip install -e ".[dev]"`).
- Artifact check (vendor files under gitignored `data/vendor/`, pinned commits in PAPER-PLAN.md): Mem0's 94.4/94.8/92.5/91.8 have no file; committed files give 467/500, 452/500, 1410/1540, 1273/1540 (PR #8 changed README only). Zep 2025 LoCoMo 75.14 adds up (1157/1540). Zep paper LME 71.2, Zep 2026 site, Supermemory, Letta: no per-question file. LoCoMo category 2/3 labels differ between Zep and Mem0.
- Prior work: no pre-emption (EvalMem tests other systems; Maximem is a competitor blog). Sources read via summarising fetch; read directly before citing.
- Not pushed on purpose: the commits name a vendor and TMLR is double blind. Zaid decides push timing.

Next (Zaid said "I will decide later"): either a local Ollama re-judge of Mem0's committed answers (free, hours of GPU, check no peer is using Ollama) or a write-up of the artifact check first. Open decisions: email Mem0 about the PR #8 files (he writes it), platform runs stay skipped ($0 + terms).

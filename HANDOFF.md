# claimledger handoff (2026-11-10)

State: main pushed to private zaidwhy/claimledger (remote created by Zaid 2026-11-10). 28 tests pass. data/ is gitignored; results/ commits only the seed-0 reports the README cites.

Finding: MemPalace's "96.6% R@5 raw" reproduces exactly (483/500, all settings matched). Plain BM25 gets 95.2% (476/500) on the same questions; 19 vs 12 discordant questions, exact McNemar p = 0.28, so k=5 recall on LongMemEval-S does not separate the two. BM25 leads at k=1 and k=3.

Next (Zaid's call, outward-facing): decide whether anything goes on MemPalace#27. Nothing has been posted.

2026-11-10 afternoon: Zaid said to launch. Headline numbers recomputed from the two committed 500-question reports (483 vs 476, 19 vs 12 discordant, p = 0.281; k=1 403 vs 413, k=3 463 vs 466, k=10 491 vs 485) and the README now states the result under the thesis. Checked live: MemPalace README still claims 96.6%, #27 open with 234 thumbs-up and 39 comments, none mentioning BM25. The repo is still PRIVATE: the permission classifier blocks the visibility change, so Zaid runs `gh repo edit zaidwhy/claimledger --visibility public --accept-visibility-change-consequences`, then writes the #27 comment himself.

## Overnight decisions (review)
- No per-question process isolation added. The earlier 500-run crash happened at 358 MB free disk; the rerun at about 10 GB free finished with 0 errors, so the fix was disk space, not code.
- Committed the 6 seed-0 reports the README cites (results/*_n50_* and *_n500_*, about 0.6 MB) so its numbers trace to files; the repo is private, so nothing is published. Other results stay ignored.

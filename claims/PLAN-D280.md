# D-280 plan: mem0, Zep, Letta claims versus measured (written 2026-11-17, nothing has been run)

Claim files: `claims/mem0.yaml`, `claims/zep.yaml`, `claims/letta.yaml` (MemPalace is already measured, `claims/mempalace.yaml`).
Every number there was read live from the cited URL on 2026-11-17. Cost figures below are estimates from the token counts the
vendors publish; per-token prices are from memory and must be re-checked before any spend.

## What kind of claim these are

MemPalace claimed retrieval recall, which claimledger measures directly (no LLM). The three libraries below claim **end-to-end QA
accuracy judged by an LLM** (LoCoMo 1540 questions, LongMemEval 500). claimledger's `compare` checks metric and judge and will print
`NOT COMPARED` against a retrieval-recall run, correctly. A fair reproduction therefore needs an answer model plus a judge, not a
new retrieval adapter. The existing `Adapter` interface (`ingest` / `search` returning session ids) can still give a retrieval-only
number for mem0 or Graphiti as a secondary, clearly labelled measurement, but that number is never a reproduction of these claims.

## mem0

- Claim: LoCoMo 92.5 (1425/1540) and LongMemEval 94.4 (472/500), top-200, single pass, from README "New Memory Algorithm (April 2026)".
- Stated caveat (verbatim in the claim file): scores are for the managed platform with "proprietary optimizations not available in the
  open-source SDK". So the headline cannot be reproduced with the OSS library by construction. Only the platform (needs a Mem0 key) or
  the OSS stack's own published numbers (LongMemEval 88.6 to 91.0 depending on extraction model) can be checked.
- Fair setting: harness `mem0ai/memory-benchmarks` (Apache 2.0, the repo the README points to), answer LLM gpt-4o, judge gpt-4o,
  top-k 200, embedder text-embedding-3-small. Judge/answer defaults are from that repo's README, not from Mem0's README.
- Free local: not the claim. OSS mem0 with Ollama (qwen2.5 extractor, nomic-embed-text) plus a local judge would be a different stack and
  must be labelled so. The harness's OSS path needs Docker Compose and an OpenAI key by default; Docker is heavy for this machine today.
- Needs money/keys: OpenAI key (answer + judge, and extraction on the OSS path). Rough scale: LoCoMo 1540 questions x about 7k context
  tokens is about 11M answer input tokens; LongMemEval 500 x 6.8k is about 3.4M, plus extraction of 500 x about 115k = about 57M tokens
  if every haystack is ingested. Order of magnitude tens of dollars on gpt-4o-class pricing; LoCoMo alone is cheaper to ingest than LongMemEval.
  Run LoCoMo first, one conversation, to measure real cost before scaling.
- Exact first command (no cost, read-only): `git clone https://github.com/mem0ai/memory-benchmarks C:/Users/Asus/projects/_ext/memory-benchmarks`
  then read its README and `benchmarks/locomo/run.py` flags. First paid command, only after Zaid approves a budget:
  `python -m benchmarks.locomo.run --project-name d280-smoke --backend cloud --mem0-api-key $MEM0_API_KEY` limited to one conversation
  (flag to be confirmed from the cloned repo; not verified).

## Zep (incl. Graphiti)

- Claims: paper (Jan 2025) DMR 94.8 vs 93.4 and LongMemEval gpt-4o 71.2 (BGE-m3, 10 nodes/edges, judge GPT-4o); website (dateModified
  2026-11-04) LoCoMo 94.7 and LongMemEval 90.2 with gpt-5.4 as reader and judge, multi-scope retrieval, no date, no code on the page.
- Graphiti is the Apache-2.0 OSS engine behind the paper; its README has no numbers. The 2026 numbers come from Zep Cloud.
- Fair setting for the 2026 claim: Zep Cloud, reader and judge gpt-5.4, 20 edges / 10 nodes / 10 episodes / 5 summaries / 5 observations.
  The public harness `getzep/zep/benchmarks/locomo` uses a different config (edge_limit 15, node_limit 5, model gpt-6-luna), so
  running it is a measurement of that config, not of the page's claim. The paper's 2025 setting (gpt-4o-mini/gpt-4o, BGE-m3) could be
  approximated with Graphiti locally but needs an LLM for graph construction (gpt-4o-mini in the paper) and a graph DB (Neo4j or FalkorDB).
- Free local: Graphiti with Ollama is possible in principle, but extraction quality with a small local model differs from gpt-4o-mini, so it
  would not reproduce the 2025 number. Not planned for now (Neo4j plus Ollama is also memory-heavy).
- Terms are the blocker, see below: Zep's customer terms bar public benchmarking of the service.
- Exact first command (read-only): `gh api repos/getzep/zep/contents/benchmarks/locomo/experiments --jq '.[].name'` and read the
  committed `experiment_2025120*` results to see what Zep published for the open harness; no run until terms are resolved.

## Letta

- Claim: LoCoMo 74.0% with a filesystem agent on GPT-4o mini (blog, 2025-08-12). Judge, scoring method and top-k are not stated.
- The Letta repo `letta-ai/letta` no longer holds the server (README points to `letta-code`; V1 is on the `archive` branch). No
  benchmark harness was found in the repo README. The claim is an agentic-loop result (agent decides which file tools to call).
- This claim cannot be fairly reproduced as stated: the judge and scoring are unspecified, so any judge we pick is a different setting,
  and `compare` would have to refuse. What can be done: re-run the blog's described setup (files plus grep/search tools, gpt-4o-mini) with an
  explicitly named judge and report it as a new measurement, not a reproduction. That requires the archived server or a rebuilt harness
  (a real build, not a scaffold) and an OpenAI key.
- Exact first command (read-only): `curl -sL https://www.letta.com/blog/benchmarking-ai-agent-memory` and check whether the post links a repo
  or script; if none, the claim is recorded as not reproducible and no run is started.

## Local free retrieval-only side measurement (optional, not a reproduction)

Using the existing adapter interface on the existing LongMemEval-S slice, a mem0-OSS retrieval adapter (embedder only, `infer=False`
style insertion, so no LLM extraction) would give recall_any@5 next to bm25 and embed. It would measure vector storage in mem0 only and
bypass the extraction and entity-linking the claim depends on, so it should be labelled `pipeline: mem0_oss_raw` if built. Not scaffolded
this phase: the mem0 OSS API (v3 migration) was not read, and a scaffold without a verified API would be a guess.

## Terms findings (read 2026-11-17)

- Licences: mem0, zep, graphiti and letta repos all carry an Apache License 2.0 LICENSE file (header checked; graphiti SPDX reported Apache-2.0
  by the GitHub API). `mem0ai/memory-benchmarks` is stated as Apache 2.0 in its README. Apache 2.0 places no limit on benchmarking or
  publishing results of the OSS code.
- Zep customer terms (https://www.getzep.com/legal/terms, section 2.3(i)): customers may not "engage in competitive analysis or benchmarking
  for public or third-party disclosure", with an exception for testing "solely for its own internal evaluation purposes". Running
  Zep Cloud and publishing the results would need Zep's written consent. Running the Apache-2.0 Graphiti locally is outside that clause
  (it binds Zep Cloud customers); publishing Graphiti-only results is allowed by the licence, but they are not the cloud claim.
- Mem0 terms (https://mem0.ai/terms, section 2.3): the fetch reported a restriction on customers to "otherwise engage in competitive analysis or
  benchmarking", with no stated carve-out for internal evaluation. The fetch tool summarises pages, so read the section directly before any
  platform run; publishing results from the Mem0 Platform is likely restricted, the OSS SDK (Apache 2.0) is not.
- Letta terms (https://www.letta.com/terms-of-service): no clause on benchmarking found by the fetch.
- Consequence: platform results (Mem0 Platform, Zep Cloud) should be measured only if Zep/Mem0 permit it in writing or if Zaid decides to keep
  results private; the publishable path is OSS-only runs, clearly labelled as not the platform claim.
- Not legal advice; the terms pages were read through a summarising fetch and should be read in full by Zaid before any platform run.

## Order of work when runs are approved

1. Mem0: clone memory-benchmarks (free), inspect flags, estimate cost for one LoCoMo conversation, then ask Zaid for a key and budget.
2. Zep: decide the terms question first; if blocked, record the claim as measured-by-nobody-independent and stop.
3. Letta: confirm whether a reproducible harness exists; if not, mark the claim not reproducible.

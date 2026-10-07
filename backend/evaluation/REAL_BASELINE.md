# Real retrieval baseline

This benchmark freezes 25 natural-language queries against the 21-page Synapse
dataset captured on October 6, 2026. Labels were defined before running the
queries against Synapse, so the benchmark is not tuned to known search results.

The cases intentionally mix direct topics, paraphrases, vague memories, overlapping
sources, and confusing neighboring topics.

Run from `backend/` in the normal Synapse environment:

```bash
python evaluation/run_retrieval_benchmark.py
```

The runner uses the same embedding model, pgvector chunk ranking, and 4B
page-deduplication logic as the application. It prints every expected/retrieved
page-ID list before reporting Hit Rate@5, Recall@5, and MRR.

It also refuses to run if expected page IDs are missing from the connected
database. Do not put database credentials in this directory or in GitHub Actions.
The live benchmark is intentionally local because CI has no Supabase secrets.

## Legacy consistency repair

The first baseline exposed pages 1-4 with zero chunk rows. Preserve that 0.800 / 0.800 / 0.800 result as the initial baseline. Before judging retrieval quality, rebuild only those legacy pages from their already-stored canonical content:

```bash
python -m evaluation.reprocess_pages 1 2 3 4
python -m evaluation.reprocess_pages 1 2 3 4 --apply
python -m evaluation.run_retrieval_benchmark
```

The first command is a dry run. The apply operation is transactional: it deletes/replaces chunks for the requested pages and commits only after all requested pages are rebuilt. The benchmark cases and labels must remain unchanged for the post-repair comparison.

## Measured results

The first frozen 25-query run produced:

- Hit Rate@5: **0.800**
- Recall@5: **0.800**
- MRR: **0.800**

Inspection showed that legacy pages 1-4 had no chunk rows. Pages 1-3 were synthetic seed records with only 74, 120, and 132 characters of stored content, while page 4 was a real Python documentation capture with 7,745 characters. Page 4 was rebuilt from its stored content; pages 1-3 were intentionally left unchanged rather than treating synthetic seed rows as representative captured webpages.

Re-running the exact same frozen benchmark after rebuilding page 4 produced:

- Hit Rate@5: **0.840**
- Recall@5: **0.840**
- MRR: **0.820**

For the 21-query captured-page subset that excludes the four cases dependent on synthetic pages 1-3, the same run produced:

- Hit Rate@5: **1.000**
- Recall@5: **1.000**
- MRR: **0.976**

The captured-page subset is a small benchmark and should not be interpreted as universal search quality. Its purpose is to show that, on the current representative dataset, the dominant observed failure was data consistency rather than an immediate need to replace the embedding model or ranking algorithm.

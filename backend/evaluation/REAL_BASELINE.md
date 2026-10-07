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

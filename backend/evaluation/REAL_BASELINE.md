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

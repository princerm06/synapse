# Synapse retrieval evaluation

Milestone 4C adds a small, reproducible evaluation harness for semantic retrieval.
It measures whether the correct saved source appears near the top of a ranked
result list instead of judging search quality only by eye.

## Metrics

- **Hit Rate@K**: fraction of queries with at least one relevant source in the top K.
- **Recall@K**: fraction of all labeled relevant sources recovered in the top K, averaged across queries.
- **MRR (Mean Reciprocal Rank)**: rewards putting the first relevant source closer to rank 1.

The metric implementation lives in `app/services/evaluation.py` and is covered by
unit tests. It intentionally accepts ranked page IDs rather than importing the
FastAPI/database stack, so metric behavior is deterministic and CI does not need
Supabase credentials or an embedding-model download.

## Building the first real benchmark

The next verification step is to label a small set of queries against pages that
have actually been saved in Synapse. Each case should contain:

1. a natural query someone would genuinely type;
2. one or more page IDs that are genuinely relevant to that query;
3. no answer text generated from the search results.

Start with roughly 15-25 queries across different saved sources. Include easy
queries, paraphrases, and a few ambiguous queries. Keep this benchmark checked in
only if its source text and labels are safe to store in the repository.

A live runner can then execute the existing Synapse retrieval pipeline for each
query, collect the ranked `page_id` values, and pass those rankings to
`evaluate_rankings`. That live benchmark should be run in an environment that
already has the normal Synapse database and embedding dependencies; CI should not
receive production database secrets merely to calculate metrics.

## Why this split exists

CI verifies that the evaluation math cannot silently regress. The real benchmark
verifies search quality against representative Synapse data. Keeping those jobs
separate prevents a unit-test workflow from gaining database credentials while
still giving us objective retrieval metrics to compare future chunking, embedding,
hybrid-search, and reranking changes.

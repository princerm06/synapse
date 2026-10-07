import argparse
import json
from pathlib import Path

from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.page_db import Page
from app.models.page_chunk_db import PageChunk
from app.services.embeddings import generate_embedding
from app.services.evaluation import EvaluationCase, evaluate_rankings
from app.services.retrieval import format_search_results


DEFAULT_BENCHMARK = Path(__file__).with_name("retrieval_benchmark.json")


def load_cases(path: Path) -> list[EvaluationCase]:
    data = json.loads(path.read_text())
    return [
        EvaluationCase(
            query=item["query"],
            relevant_page_ids=frozenset(item["relevant_page_ids"]),
        )
        for item in data
    ]


def retrieve_page_ids(db: Session, query: str, limit: int = 5) -> list[int]:
    query_embedding = generate_embedding(query)
    distance = PageChunk.embedding.cosine_distance(query_embedding)

    rows = (
        db.query(PageChunk, Page, distance.label("distance"))
        .join(Page, PageChunk.page_id == Page.id)
        .filter(PageChunk.embedding.is_not(None))
        .order_by(distance)
        .limit(50)
        .all()
    )

    results = format_search_results(rows, limit=limit)
    return [result["page_id"] for result in results]


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Synapse's labeled retrieval benchmark.")
    parser.add_argument("--benchmark", type=Path, default=DEFAULT_BENCHMARK)
    parser.add_argument("--k", type=int, default=5)
    args = parser.parse_args()

    cases = load_cases(args.benchmark)
    evaluated = []

    with SessionLocal() as db:
        existing_ids = {page_id for (page_id,) in db.query(Page.id).all()}
        required_ids = set().union(*(case.relevant_page_ids for case in cases))
        missing_ids = sorted(required_ids - existing_ids)
        if missing_ids:
            raise RuntimeError(
                "Benchmark dataset does not match this database. "
                f"Missing expected page IDs: {missing_ids}"
            )

        for case in cases:
            ranked_ids = retrieve_page_ids(db, case.query, limit=args.k)
            evaluated.append((case, ranked_ids))
            print(
                f"{case.query}\n"
                f"  expected: {sorted(case.relevant_page_ids)}\n"
                f"  retrieved: {ranked_ids}\n"
            )

    metrics = evaluate_rankings(evaluated, k=args.k)
    print("=== Synapse retrieval baseline ===")
    print(f"Queries: {metrics.query_count}")
    print(f"Hit Rate@{args.k}: {metrics.hit_rate_at_k:.3f}")
    print(f"Recall@{args.k}: {metrics.recall_at_k:.3f}")
    print(f"MRR: {metrics.mean_reciprocal_rank:.3f}")


if __name__ == "__main__":
    main()

from dataclasses import dataclass
from typing import Iterable, Sequence


@dataclass(frozen=True)
class EvaluationCase:
    """One retrieval query with the source pages considered relevant."""

    query: str
    relevant_page_ids: frozenset[int]


@dataclass(frozen=True)
class EvaluationMetrics:
    query_count: int
    hit_rate_at_k: float
    recall_at_k: float
    mean_reciprocal_rank: float


def reciprocal_rank(ranked_page_ids: Sequence[int], relevant_page_ids: set[int] | frozenset[int]) -> float:
    """Return 1/rank for the first relevant result, or 0 when none is retrieved."""
    for rank, page_id in enumerate(ranked_page_ids, start=1):
        if page_id in relevant_page_ids:
            return 1.0 / rank
    return 0.0


def recall_at_k(ranked_page_ids: Sequence[int], relevant_page_ids: set[int] | frozenset[int], k: int) -> float:
    """Return the fraction of relevant pages present in the first k results."""
    if k <= 0:
        raise ValueError("k must be greater than 0")
    if not relevant_page_ids:
        raise ValueError("relevant_page_ids cannot be empty")

    retrieved = set(ranked_page_ids[:k])
    return len(retrieved.intersection(relevant_page_ids)) / len(relevant_page_ids)


def evaluate_rankings(
    cases: Iterable[tuple[EvaluationCase, Sequence[int]]],
    k: int = 5,
) -> EvaluationMetrics:
    """Aggregate standard retrieval metrics over precomputed ranked page IDs.

    The evaluator is deliberately independent of the database and embedding model,
    making the metric definitions deterministic and easy to regression test. A
    separate runner can feed it rankings produced by the live Synapse search stack.
    """
    if k <= 0:
        raise ValueError("k must be greater than 0")

    evaluated = list(cases)
    if not evaluated:
        raise ValueError("at least one evaluation case is required")

    hit_sum = 0.0
    recall_sum = 0.0
    reciprocal_rank_sum = 0.0

    for case, ranked_page_ids in evaluated:
        if not case.relevant_page_ids:
            raise ValueError("each evaluation case needs at least one relevant page")

        top_k = ranked_page_ids[:k]
        hit_sum += float(any(page_id in case.relevant_page_ids for page_id in top_k))
        recall_sum += recall_at_k(ranked_page_ids, case.relevant_page_ids, k)
        reciprocal_rank_sum += reciprocal_rank(ranked_page_ids, case.relevant_page_ids)

    count = len(evaluated)
    return EvaluationMetrics(
        query_count=count,
        hit_rate_at_k=hit_sum / count,
        recall_at_k=recall_sum / count,
        mean_reciprocal_rank=reciprocal_rank_sum / count,
    )

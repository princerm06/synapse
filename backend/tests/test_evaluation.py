import pytest

from app.services.evaluation import (
    EvaluationCase,
    evaluate_rankings,
    recall_at_k,
    reciprocal_rank,
)


def test_reciprocal_rank_uses_first_relevant_result():
    assert reciprocal_rank([8, 4, 2, 9], {2, 9}) == pytest.approx(1 / 3)


def test_reciprocal_rank_is_zero_when_relevant_source_is_missing():
    assert reciprocal_rank([8, 4, 2], {7}) == 0.0


def test_recall_at_k_supports_multiple_relevant_sources():
    assert recall_at_k([1, 3, 8, 5], {1, 5}, k=3) == 0.5
    assert recall_at_k([1, 3, 8, 5], {1, 5}, k=4) == 1.0


def test_evaluate_rankings_aggregates_hit_recall_and_mrr():
    cases = [
        (
            EvaluationCase("fastapi response models", frozenset({10})),
            [10, 20, 30],
        ),
        (
            EvaluationCase("cnn overfitting", frozenset({40, 50})),
            [99, 50, 40],
        ),
        (
            EvaluationCase("unseen topic", frozenset({70})),
            [80, 90, 100],
        ),
    ]

    metrics = evaluate_rankings(cases, k=2)

    assert metrics.query_count == 3
    assert metrics.hit_rate_at_k == pytest.approx(2 / 3)
    assert metrics.recall_at_k == pytest.approx((1 + 0.5 + 0) / 3)
    assert metrics.mean_reciprocal_rank == pytest.approx((1 + 0.5 + 0) / 3)


def test_evaluator_rejects_invalid_inputs():
    with pytest.raises(ValueError):
        recall_at_k([1], {1}, k=0)

    with pytest.raises(ValueError):
        recall_at_k([1], set(), k=1)

    with pytest.raises(ValueError):
        evaluate_rankings([], k=5)

    with pytest.raises(ValueError):
        evaluate_rankings(
            [(EvaluationCase("query", frozenset()), [1, 2])],
            k=5,
        )

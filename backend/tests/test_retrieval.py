from datetime import datetime, timezone
from types import SimpleNamespace

from app.services.retrieval import clean_excerpt, format_search_results


def make_page(page_id: int, title: str = "Source"):
    return SimpleNamespace(
        id=page_id,
        url=f"https://example.com/{page_id}",
        title=title,
        created_at=datetime(2026, 10, 5, tzinfo=timezone.utc),
    )


def make_chunk(chunk_id: int, index: int, content: str):
    return SimpleNamespace(
        id=chunk_id,
        chunk_index=index,
        content=content,
    )


def test_clean_excerpt_collapses_whitespace():
    text = "A useful sentence.\n\n   Another    useful sentence."

    assert clean_excerpt(text) == "A useful sentence. Another useful sentence."


def test_clean_excerpt_truncates_on_word_boundary():
    excerpt = clean_excerpt("alpha beta gamma delta epsilon", max_length=18)

    assert excerpt == "alpha beta gamma…"
    assert len(excerpt) <= 19


def test_results_keep_only_best_chunk_per_page():
    page_one = make_page(1, "First source")
    page_two = make_page(2, "Second source")

    rows = [
        (make_chunk(10, 2, "Best chunk from first source."), page_one, 0.10),
        (make_chunk(11, 4, "Another chunk from first source."), page_one, 0.15),
        (make_chunk(20, 0, "Best chunk from second source."), page_two, 0.20),
    ]

    results = format_search_results(rows)

    assert len(results) == 2
    assert results[0]["page_id"] == 1
    assert results[0]["matched_chunk_id"] == 10
    assert results[0]["matched_chunk_index"] == 2
    assert results[1]["page_id"] == 2


def test_results_expose_excerpt_instead_of_raw_content():
    page = make_page(1)
    chunk = make_chunk(10, 0, "word " * 100)

    result = format_search_results([(chunk, page, 0.25)], excerpt_length=40)[0]

    assert "excerpt" in result
    assert "content" not in result
    assert result["excerpt"].endswith("…")
    assert result["similarity"] == 0.75


def test_result_limit_counts_unique_pages():
    rows = []
    for page_id in range(1, 8):
        rows.append(
            (
                make_chunk(page_id, 0, f"Chunk for page {page_id}"),
                make_page(page_id),
                page_id / 100,
            )
        )

    results = format_search_results(rows, limit=5)

    assert len(results) == 5
    assert [result["page_id"] for result in results] == [1, 2, 3, 4, 5]


def test_similarity_is_clamped_to_cosine_range():
    page = make_page(1)
    chunk = make_chunk(1, 0, "content")

    high = format_search_results([(chunk, page, -1.0)])[0]
    low = format_search_results([(chunk, page, 3.0)])[0]

    assert high["similarity"] == 1.0
    assert low["similarity"] == -1.0

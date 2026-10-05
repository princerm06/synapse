import re
from typing import Any, Iterable


_WHITESPACE = re.compile(r"\s+")


def clean_excerpt(text: str, max_length: int = 360) -> str:
    """Return a compact, readable excerpt without cutting a word in half."""
    cleaned = _WHITESPACE.sub(" ", text).strip()

    if len(cleaned) <= max_length:
        return cleaned

    cutoff = cleaned.rfind(" ", 0, max_length + 1)
    if cutoff <= 0:
        cutoff = max_length

    return cleaned[:cutoff].rstrip(" ,;:-") + "…"


def format_search_results(
    rows: Iterable[tuple[Any, Any, float]],
    limit: int = 5,
    excerpt_length: int = 360,
) -> list[dict[str, Any]]:
    """Keep the strongest chunk per page and expose a stable search-result shape.

    Rows are expected in ascending vector-distance order. The first occurrence of
    a page is therefore its strongest chunk. This prevents one long source from
    occupying every visible result while retaining chunk-level provenance.
    """
    results: list[dict[str, Any]] = []
    seen_page_ids: set[int] = set()

    for chunk, page, distance_value in rows:
        if page.id in seen_page_ids:
            continue

        seen_page_ids.add(page.id)
        similarity = max(-1.0, min(1.0, 1 - float(distance_value)))

        results.append(
            {
                "page_id": page.id,
                "matched_chunk_id": chunk.id,
                "matched_chunk_index": chunk.chunk_index,
                "url": page.url,
                "title": page.title,
                "excerpt": clean_excerpt(chunk.content, excerpt_length),
                "created_at": page.created_at,
                "similarity": similarity,
            }
        )

        if len(results) >= limit:
            break

    return results

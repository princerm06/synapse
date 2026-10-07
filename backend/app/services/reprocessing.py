from collections.abc import Callable
from typing import Any

from app.models.page_chunk_db import PageChunk
from app.models.page_db import Page
from app.services.chunking import chunk_text


def rebuild_page_chunks(
    db: Any,
    page: Page,
    *,
    embedder: Callable[[str], list[float]] | None = None,
) -> int:
    """Replace a page's chunks using its currently stored canonical content."""
    if embedder is None:
        # Keep the heavyweight sentence-transformers dependency out of import-time
        # paths used by lightweight unit tests and maintenance tooling discovery.
        from app.services.embeddings import generate_embedding

        embedder = generate_embedding

    chunks = chunk_text(page.content)

    db.query(PageChunk).filter(PageChunk.page_id == page.id).delete(
        synchronize_session=False
    )

    for index, chunk in enumerate(chunks):
        db.add(
            PageChunk(
                page_id=page.id,
                chunk_index=index,
                content=chunk,
                embedding=embedder(chunk),
            )
        )

    return len(chunks)

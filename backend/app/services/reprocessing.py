from sqlalchemy.orm import Session

from app.models.page_chunk_db import PageChunk
from app.models.page_db import Page
from app.services.chunking import chunk_text
from app.services.embeddings import generate_embedding


def rebuild_page_chunks(db: Session, page: Page) -> int:
    """Replace a page's chunks using its currently stored canonical content."""
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
                embedding=generate_embedding(chunk),
            )
        )

    return len(chunks)

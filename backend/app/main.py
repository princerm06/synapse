from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.page import PageCreate
from app.models.page_db import Page
from app.models.page_chunk_db import PageChunk
from app.services.chunking import chunk_text
from app.services.embeddings import generate_embedding
from app.services.retrieval import format_search_results


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": "Synapse backend is running"}


@app.get("/health")
def health():
    return {"status": "ok", "environment": settings.app_env}


@app.post("/pages")
def create_page(page: PageCreate, db: Session = Depends(get_db)):
    db_page = (
        db.query(Page)
        .filter(Page.url == page.url)
        .first()
    )

    if db_page is None:
        db_page = Page(
            url=page.url,
            title=page.title,
            content=page.content,
            embedding=generate_embedding(page.content),
        )

        db.add(db_page)
        db.commit()
        db.refresh(db_page)
    else:
        db_page.title = page.title
        db_page.content = page.content
        db_page.embedding = generate_embedding(page.content)

        db.query(PageChunk).filter(
            PageChunk.page_id == db_page.id
        ).delete(synchronize_session=False)

        db.commit()

    chunks = chunk_text(page.content)

    for index, chunk in enumerate(chunks):
        db_chunk = PageChunk(
            page_id=db_page.id,
            chunk_index=index,
            content=chunk,
            embedding=generate_embedding(chunk),
        )
        db.add(db_chunk)

    db.commit()

    return {
        "id": db_page.id,
        "url": db_page.url,
        "title": db_page.title,
        "content": db_page.content,
        "created_at": db_page.created_at,
        "chunks_created": len(chunks),
    }


@app.get("/search")
def search_pages(query: str, db: Session = Depends(get_db)):
    query_embedding = generate_embedding(query)
    distance = PageChunk.embedding.cosine_distance(query_embedding)

    # Fetch more chunk candidates than we display because several of the best
    # chunks can belong to the same source page. format_search_results keeps only
    # the strongest chunk from each page.
    candidate_limit = 50
    result_limit = 5

    rows = (
        db.query(PageChunk, Page, distance.label("distance"))
        .join(Page, PageChunk.page_id == Page.id)
        .filter(PageChunk.embedding.is_not(None))
        .order_by(distance)
        .limit(candidate_limit)
        .all()
    )

    return format_search_results(rows, limit=result_limit)

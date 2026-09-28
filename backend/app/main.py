from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.page import PageCreate
from app.models.page_db import Page
from app.services.embeddings import generate_embedding


app = FastAPI()


@app.get("/")
def root():
    return {"message": "Synapse backend is running"}


@app.post("/pages")
def create_page(page: PageCreate, db: Session = Depends(get_db)):
    db_page = Page(
        url=page.url,
        title=page.title,
        content=page.content,
        embedding=generate_embedding(page.content),
    )

    db.add(db_page)
    db.commit()
    db.refresh(db_page)

    return db_page


@app.get("/search")
def search_pages(query: str, db: Session = Depends(get_db)):
    query_embedding = generate_embedding(query)

    distance = Page.embedding.cosine_distance(query_embedding)

    results = (
        db.query(Page, distance.label("distance"))
        .filter(Page.embedding.is_not(None))
        .order_by(distance)
        .limit(5)
        .all()
    )

    return [
        {
            "id": page.id,
            "url": page.url,
            "title": page.title,
            "content": page.content,
            "created_at": page.created_at,
            "similarity": 1 - float(distance_value),
        }
        for page, distance_value in results
    ]
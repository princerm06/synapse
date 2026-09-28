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
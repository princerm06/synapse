from fastapi import FastAPI
from app.models.page import PageCreate

app = FastAPI()


@app.get("/")
def root():
    return {"message": "Synapse backend is running"}


@app.post("/pages")
def create_page(page: PageCreate):
    return page
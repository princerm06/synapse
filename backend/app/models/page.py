from pydantic import BaseModel


class PageCreate(BaseModel):
    url: str
    title: str
    content: str
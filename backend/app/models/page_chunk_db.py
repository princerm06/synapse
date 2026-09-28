from sqlalchemy import BigInteger, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column
from pgvector.sqlalchemy import Vector

from app.models.page_db import Base


class PageChunk(Base):
    __tablename__ = "page_chunks"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
    )

    page_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("pages.id", ondelete="CASCADE"),
        nullable=False,
    )

    chunk_index: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    embedding: Mapped[list[float]] = mapped_column(
        Vector(384),
        nullable=False,
    )
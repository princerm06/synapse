from types import SimpleNamespace
from unittest.mock import Mock, patch

from app.services.reprocessing import rebuild_page_chunks


def test_rebuild_page_chunks_deletes_old_chunks_and_adds_new_ones():
    db = Mock()
    query = db.query.return_value
    query.filter.return_value.delete.return_value = 2
    page = SimpleNamespace(id=42, content="First paragraph.\n\nSecond paragraph.")
    embeddings = iter([[0.1] * 384, [0.2] * 384])

    with patch(
        "app.services.reprocessing.chunk_text",
        return_value=["first", "second"],
    ):
        count = rebuild_page_chunks(
            db,
            page,
            embedder=lambda _text: next(embeddings),
        )

    assert count == 2
    query.filter.return_value.delete.assert_called_once_with(
        synchronize_session=False
    )
    assert db.add.call_count == 2

    added = [call.args[0] for call in db.add.call_args_list]
    assert [chunk.page_id for chunk in added] == [42, 42]
    assert [chunk.chunk_index for chunk in added] == [0, 1]
    assert [chunk.content for chunk in added] == ["first", "second"]


def test_rebuild_page_chunks_allows_empty_content_result():
    db = Mock()
    query = db.query.return_value
    page = SimpleNamespace(id=7, content="")

    with patch("app.services.reprocessing.chunk_text", return_value=[]):
        count = rebuild_page_chunks(db, page, embedder=lambda _text: [])

    assert count == 0
    query.filter.return_value.delete.assert_called_once_with(
        synchronize_session=False
    )
    db.add.assert_not_called()

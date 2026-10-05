import pytest

from app.services.chunking import chunk_text


def test_empty_text_returns_no_chunks():
    assert chunk_text("   \n\n  ") == []


def test_short_paragraphs_preserve_boundaries():
    text = "First paragraph has useful context.\n\nSecond paragraph stays separate."

    chunks = chunk_text(text, chunk_size=100, overlap=0)

    assert chunks == [
        "First paragraph has useful context.\n\nSecond paragraph stays separate."
    ]


def test_paragraphs_are_not_cut_at_arbitrary_characters():
    first = "A" * 60
    second = "B" * 60

    chunks = chunk_text(f"{first}\n\n{second}", chunk_size=100, overlap=0)

    assert chunks == [first, second]


def test_oversized_paragraph_splits_on_sentences():
    text = (
        "FastAPI validates response data. "
        "Response models document the API contract. "
        "Type annotations improve editor support."
    )

    chunks = chunk_text(text, chunk_size=70, overlap=0)

    assert all(len(chunk) <= 70 for chunk in chunks)
    assert "FastAPI validates response data." in chunks[0]
    assert all(not chunk.startswith("API contract") for chunk in chunks)


def test_long_sentence_falls_back_to_word_boundaries():
    text = "alpha beta gamma delta epsilon zeta eta theta iota kappa lambda"

    chunks = chunk_text(text, chunk_size=25, overlap=0)

    assert all(len(chunk) <= 25 for chunk in chunks)
    assert "".join(chunks).replace(" ", "") == text.replace(" ", "")


def test_overlap_reuses_complete_trailing_paragraphs():
    first = "First paragraph." * 3
    second = "Second paragraph."
    third = "Third paragraph." * 3

    chunks = chunk_text(
        f"{first}\n\n{second}\n\n{third}",
        chunk_size=85,
        overlap=25,
    )

    assert len(chunks) >= 2
    assert chunks[0].endswith(second)
    assert chunks[1].startswith(second)


def test_invalid_chunk_configuration_is_rejected():
    with pytest.raises(ValueError):
        chunk_text("text", chunk_size=0)

    with pytest.raises(ValueError):
        chunk_text("text", chunk_size=100, overlap=-1)

    with pytest.raises(ValueError):
        chunk_text("text", chunk_size=100, overlap=100)

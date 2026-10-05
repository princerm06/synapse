import re


_SENTENCE_BOUNDARY = re.compile(r"(?<=[.!?])\s+")


def _normalize_block(block: str) -> str:
    """Collapse noisy whitespace inside a paragraph while preserving its boundary."""
    return " ".join(block.split())


def _split_oversized_block(block: str, chunk_size: int) -> list[str]:
    """Split a long paragraph on sentence boundaries, then words as a fallback."""
    if len(block) <= chunk_size:
        return [block]

    sentences = [
        sentence.strip()
        for sentence in _SENTENCE_BOUNDARY.split(block)
        if sentence.strip()
    ]

    pieces: list[str] = []
    current = ""

    for sentence in sentences:
        if len(sentence) > chunk_size:
            if current:
                pieces.append(current)
                current = ""

            words = sentence.split()
            word_piece = ""

            for word in words:
                candidate = f"{word_piece} {word}".strip()
                if word_piece and len(candidate) > chunk_size:
                    pieces.append(word_piece)
                    word_piece = word
                else:
                    word_piece = candidate

            if word_piece:
                pieces.append(word_piece)
            continue

        candidate = f"{current} {sentence}".strip()
        if current and len(candidate) > chunk_size:
            pieces.append(current)
            current = sentence
        else:
            current = candidate

    if current:
        pieces.append(current)

    return pieces


def _overlap_blocks(blocks: list[str], overlap: int) -> list[str]:
    """Return complete trailing blocks whose combined size fits the overlap budget."""
    if overlap <= 0:
        return []

    selected: list[str] = []
    length = 0

    for block in reversed(blocks):
        added_length = len(block) + (2 if selected else 0)
        if selected and length + added_length > overlap:
            break
        if not selected and len(block) > overlap:
            break

        selected.append(block)
        length += added_length

    selected.reverse()
    return selected


def chunk_text(
    text: str,
    chunk_size: int = 1000,
    overlap: int = 200,
) -> list[str]:
    """Chunk text while preserving paragraph and sentence boundaries when possible.

    Paragraphs are the primary structural unit. Small neighboring paragraphs are
    packed together up to ``chunk_size``. Oversized paragraphs are split at
    sentence boundaries, with word boundaries as a final fallback. Overlap reuses
    complete trailing blocks rather than slicing through arbitrary characters.
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than 0")
    if overlap < 0:
        raise ValueError("overlap cannot be negative")
    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")

    text = text.strip()
    if not text:
        return []

    raw_blocks = re.split(r"\n\s*\n+", text)
    blocks: list[str] = []

    for raw_block in raw_blocks:
        block = _normalize_block(raw_block)
        if block:
            blocks.extend(_split_oversized_block(block, chunk_size))

    if not blocks:
        return []

    chunks: list[str] = []
    current_blocks: list[str] = []

    for block in blocks:
        candidate_blocks = current_blocks + [block]
        candidate = "\n\n".join(candidate_blocks)

        if current_blocks and len(candidate) > chunk_size:
            chunks.append("\n\n".join(current_blocks))
            current_blocks = _overlap_blocks(current_blocks, overlap)

            candidate_blocks = current_blocks + [block]
            if len("\n\n".join(candidate_blocks)) > chunk_size:
                current_blocks = [block]
            else:
                current_blocks = candidate_blocks
        else:
            current_blocks = candidate_blocks

    if current_blocks:
        final_chunk = "\n\n".join(current_blocks)
        if not chunks or final_chunk != chunks[-1]:
            chunks.append(final_chunk)

    return chunks

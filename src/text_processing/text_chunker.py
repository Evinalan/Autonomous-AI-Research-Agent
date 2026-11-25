
import re


# Maximum characters in one chunk
CHUNK_SIZE = 1200

# Characters repeated between neighboring chunks
CHUNK_OVERLAP = 200


def split_text_into_chunks(text, chunk_size=CHUNK_SIZE,
                           overlap=CHUNK_OVERLAP):
    """
    Split text into manageable chunks with overlapping context.
    """

    if not text:
        return []

    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than zero.")

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError(
            "overlap must be non-negative and smaller than chunk_size."
        )

    chunks = []

    start = 0
    text_length = len(text)

    while start < text_length:

        end = min(start + chunk_size, text_length)

        if end < text_length:

            # Try to end at a sentence boundary
            sentence_end = max(
                text.rfind(". ", start, end),
                text.rfind("? ", start, end),
                text.rfind("! ", start, end)
            )

            # If no suitable sentence boundary exists,
            # try to end at a word boundary.
            if sentence_end > start + chunk_size // 2:
                end = sentence_end + 1

            else:
                word_end = text.rfind(" ", start, end)

                if word_end > start + chunk_size // 2:
                    end = word_end

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end >= text_length:
            break

        # Move forward while retaining overlapping context
        next_start = max(start + 1, end - overlap)

        # Avoid starting in the middle of a word
        next_space = text.find(" ", next_start, end)

        if next_space != -1:
            next_start = next_space + 1

        start = next_start

    return chunks

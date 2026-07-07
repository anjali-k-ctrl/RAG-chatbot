import re


def chunk_text(
    text: str,
    chunk_size: int = 700,
    overlap: int = 150
):

    # Split into sentences
    sentences = re.split(
        r'(?<=[.!?])\s+',
        text
    )

    chunks = []

    current_chunk = ""

    for sentence in sentences:

        if (
            len(current_chunk)
            + len(sentence)
            <= chunk_size
        ):

            current_chunk += (
                sentence + " "
            )

        else:

            chunks.append(
                current_chunk.strip()
            )

            # Create overlap
            overlap_text = (
                current_chunk[-overlap:]
                if len(current_chunk) > overlap
                else current_chunk
            )

            current_chunk = (
                overlap_text
                + " "
                + sentence
                + " "
            )

    if current_chunk:

        chunks.append(
            current_chunk.strip()
        )

    return chunks
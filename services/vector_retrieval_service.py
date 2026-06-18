from services.opensearch_service import (
    search_similar_chunks
)


def retrieve_context(
    query: str
):

    chunks = search_similar_chunks(
        query=query,
        k=3
    )

    if not chunks:
        return "", 0

    context = "\n\n".join(
        chunk["text"]
        for chunk in chunks
    )

    top_score = chunks[0]["score"]

    return context, top_score
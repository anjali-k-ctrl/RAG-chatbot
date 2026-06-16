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

    return "\n\n".join(chunks)
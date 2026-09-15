from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
import boto3

from config.settings import settings


def get_opensearch_client():

    credentials = boto3.Session(
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION
    ).get_credentials()

    awsauth = AWS4Auth(
        credentials.access_key,
        credentials.secret_key,
        settings.AWS_REGION,
        "aoss"
    )

    return OpenSearch(
        hosts=[
            {
                "host": settings.OPENSEARCH_HOST,
                "port": settings.OPENSEARCH_PORT
            }
        ],
        http_auth=awsauth,
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection
    )

from services.embedding_service import generate_embedding


INDEX_NAME = "mediashipper-docs"

def create_index():
    client = get_opensearch_client()

    index_body = {
        "settings": {
            "index": {
                "knn": True
            }
        },
        "mappings": {
            "properties": {
                "text": {
                    "type": "text"
                },
                "document_id": {
                    "type": "keyword"
                },
                "document_name": {
                    "type": "keyword"
                },
                "page_name": {
                    "type": "keyword"
                },
                "uploaded_at": {
                    "type": "date"
                },
                "audience": {
                    "type": "keyword"
                },
                "embedding": {
                    "type": "knn_vector",
                    "dimension": 384
                }
            }
        }
    }

    if client.indices.exists(index=INDEX_NAME):
        print(f"Deleting existing index: {INDEX_NAME}")
        client.indices.delete(index=INDEX_NAME)
        print("Old index deleted.")

    response = client.indices.create(
        index=INDEX_NAME,
        body=index_body
    )

    print("New index created successfully.")
    print(response)


def index_chunk(
    text: str,
    document_id: str,
    document_name: str,
    page_name: str,
    uploaded_at,
    audience: str
):

    client = get_opensearch_client()

    print("=" * 60)
    print("INDEXING CHUNK")
    print(document_name)
    print(page_name)
    print(text[:150])

    embedding = generate_embedding(text)

    document = {
        "text": text,
        "document_id": document_id,
        "document_name": document_name,
        "page_name": page_name,
        "uploaded_at": uploaded_at.isoformat(),
        "audience": audience,
        "embedding": embedding
    }

    response = client.index(
        index=INDEX_NAME,
        body=document
    )
    print("Indexed:", response["_id"])

    return response


def search_similar_chunks(
    query: str,
    audience: str,
    k: int = 3
):
    client = get_opensearch_client()

    query_embedding = generate_embedding(query)

    candidate_k = max(k * 3, 10)

    response = client.search(
        index=INDEX_NAME,
        body={
            "size": candidate_k,
            "query": {
                "bool": {
                    "filter": [
                        {
                            "term": {
                                "audience": audience
                            }
                        }
                    ],
                    "must": [
                        {
                            "knn": {
                                "embedding": {
                                    "vector": query_embedding,
                                    "k": candidate_k
                                }
                            }
                        }
                    ]
                }
            }
        }
    )

    results = []

    for hit in response["hits"]["hits"]:

        source = hit["_source"]

        results.append({
            "text": source["text"],
            "score": hit["_score"],
            "document_id": source.get("document_id"),
            "document_name": source["document_name"],
            "page_name": source["page_name"],
            "uploaded_at": source.get("uploaded_at"),
            "audience": source.get("audience")
        })

    # --------------------------------------------------
    # RELEVANCE-FIRST RANKING
    # --------------------------------------------------
    #
    # Relevance is always the primary signal.
    #
    # Recency is only used when two results are
    # extremely close in relevance.
    # --------------------------------------------------

    RECENCY_SCORE_GAP = 0.02

    results.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    ranked_results = []

    i = 0

    while i < len(results):

        current = results[i]

        similar_results = [current]

        j = i + 1

        while j < len(results):

            score_gap = (
                current["score"]
                - results[j]["score"]
            )

            if score_gap <= RECENCY_SCORE_GAP:

                similar_results.append(results[j])

                j += 1

            else:

                break

        # For genuinely similar scores,
        # newer documents get precedence.
        similar_results.sort(
            key=lambda x: (
                x.get("uploaded_at") or ""
            ),
            reverse=True
        )

        ranked_results.extend(similar_results)

        i = j

    final_results = ranked_results[:k]

    print("\n===== RETRIEVAL RESULTS =====")

    for rank, result in enumerate(
        final_results,
        start=1
    ):

        print(
            f"Rank: {rank} | "
            f"Score: {result['score']:.4f} | "
            f"Audience: {result['audience']} | "
            f"Uploaded: {result['uploaded_at']} | "
            f"Document ID: {result['document_id']} | "
            f"Document: {result['document_name']}"
        )

    print("=============================\n")

    return final_results

def delete_document_chunks(document_id: str):

    client = get_opensearch_client()

    print("=" * 60)
    print("DELETING OPENSEARCH CHUNKS")
    print("Index:", INDEX_NAME)
    print("Document ID:", document_id)

    response = client.search(
        index=INDEX_NAME,
        body={
            "size": 1000,
            "query": {
                "term": {
                    "document_id": document_id
                }
            }
        }
    )

    hits = response["hits"]["hits"]

    print("Matching chunks:", len(hits))

    deleted_count = 0

    for hit in hits:

        opensearch_id = hit["_id"]

        client.delete(
            index=INDEX_NAME,
            id=opensearch_id,
            refresh=False
        )

        deleted_count += 1

        print(
            f"Deleted OpenSearch chunk: {opensearch_id}"
        )

    print(
        f"Deleted {deleted_count} OpenSearch chunks "
        f"for document {document_id}"
    )

    print("=" * 60)

    return {
        "deleted": deleted_count
    }

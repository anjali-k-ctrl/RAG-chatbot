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


def index_chunk(
    text: str,
    document_name: str,
    page_name: str
):

    client = get_opensearch_client()

    embedding = generate_embedding(text)

    document = {
        "text": text,
        "document_name": document_name,
        "page_name": page_name,
        "embedding": embedding
    }

    response = client.index(
        index=INDEX_NAME,
        body=document
    )

    return response


def search_similar_chunks(
    query: str,
    k: int = 3
):

    client = get_opensearch_client()

    query_embedding = generate_embedding(query)

    response = client.search(
        index=INDEX_NAME,
        body={
            "size": k,
            "query": {
                "knn": {
                    "embedding": {
                        "vector": query_embedding,
                        "k": k
                    }
                }
            }
        }
    )

    return [
        {
            "text": hit["_source"]["text"],
            "score": hit["_score"]
        }
        for hit in response["hits"]["hits"]
    ]
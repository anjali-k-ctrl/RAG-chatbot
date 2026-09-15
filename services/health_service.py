from database.mongodb import client

from services.opensearch_service import search_similar_chunks


def check_application():
    return "healthy"


def check_mongodb():
    try:
        client.admin.command("ping")
        return "healthy"
    except Exception as e:
        print("MongoDB Health Check:", e)
        return "unhealthy"


def check_opensearch():
    try:
        search_similar_chunks(
            query="health check",
            k=1,
            audience="seller"
        )
        return "healthy"
    except Exception as e:
        print("OpenSearch Health Check:", repr(e))
        return "unhealthy"
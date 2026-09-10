from database.postgres import SessionLocal
from services.opensearch_service import get_opensearch_client
from sqlalchemy import text


def check_application():
    return "healthy"


def check_postgres():

    db = SessionLocal()

    try:

        db.execute(text("SELECT 1"))

        return "healthy"

    except Exception:

        return "unhealthy"

    finally:

        db.close()


from services.opensearch_service import search_similar_chunks


def check_opensearch():

    try:

        search_similar_chunks(
            query="health check",
            k=1
        )

        return "healthy"

    except Exception as e:

        print("OpenSearch Health Check:", e)

        return "unhealthy"
import time

from services.system_health_service import (
    log_system_health
)
from services.opensearch_service import (
    search_similar_chunks
)

# Circuit Breaker State
failure_count = 0
circuit_open = False
last_failure_time = 0

MAX_FAILURES = 3
RECOVERY_TIMEOUT = 30


def retrieve(query: str, audience: str):
    global failure_count
    global circuit_open
    global last_failure_time

    start_time = time.time()

    if circuit_open:

        elapsed = time.time() - last_failure_time

        if elapsed < RECOVERY_TIMEOUT:

            print("Circuit Breaker OPEN")

            raise Exception(
                "OpenSearch temporarily unavailable"
            )

        print("Trying OpenSearch again...")

        circuit_open = False
        failure_count = 0

    last_exception = None

    for attempt in range(3):

        try:

            print(
                f"OpenSearch Attempt {attempt + 1}"
            )

            results = search_similar_chunks(query, audience)
            print(results)

            if not results:
                return {
                    "context": "",
                    "score": 0.0,
                    "chunks": []
                }

            context = "\n\n".join(
                chunk["text"]
                for chunk in results
            )

            top_score = results[0]["score"]

            response_time = (
                time.time() - start_time
            ) * 1000

            log_system_health(
                service="OpenSearch",
                status="SUCCESS",
                question=query,
                retry_count=attempt + 1,
                circuit_open=False,
                retrieval_source="OpenSearch",
                response_time_ms=response_time
            )

            return {
                "context": context,
                "score": top_score,
                "chunks": results
            }

        except Exception as e:

            last_exception = e

            print(
                f"OpenSearch Failed: {e}"
            )

            failure_count += 1

            if failure_count >= MAX_FAILURES:

                circuit_open = True
                last_failure_time = time.time()

                print("Circuit Breaker OPENED")

            time.sleep(1)

    response_time = (
        time.time() - start_time
    ) * 1000

    log_system_health(
        service="OpenSearch",
        status="FAILED",
        question=query,
        error=str(last_exception),
        retry_count=3,
        circuit_open=circuit_open,
        retrieval_source="OpenSearch",
        response_time_ms=response_time
    )

    raise last_exception
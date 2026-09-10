from datetime import datetime


def log_opensearch_outage(question: str, error: str):

    with open(
        "logs/opensearch_outages.log",
        "a",
        encoding="utf-8"
    ) as file:

        file.write(
            f"{datetime.now()} | "
            f"{question} | "
            f"{error}\n"
        )
import csv
from datetime import datetime


def log_retrieval(
    question,
    score
):

    with open(
        "logs/retrieval_logs.csv",
        "a",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.writer(file)

        writer.writerow([
            datetime.now(),
            question,
            score
        ])
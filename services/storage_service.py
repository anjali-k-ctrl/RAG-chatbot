import os


def get_document_path(filename: str) -> str:
    return os.path.join(
        "training_docs",
        filename
    )
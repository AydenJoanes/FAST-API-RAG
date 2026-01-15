import re
from typing import List, Dict


def clean_text(text: str) -> str:
    """
    Normalize whitespace
    """
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def chunk_page(
    page_text: str,
    page_number: int,
    chunk_size: int = 500,
    overlap: int = 50
) -> List[Dict]:
    """
    Chunk a single page and attach metadata
    """
    chunks = []
    cleaned_text = clean_text(page_text)

    start = 0
    length = len(cleaned_text)
    chunk_id = 0

    while start < length:
        end = start + chunk_size
        chunk_text = cleaned_text[start:end]

        chunks.append({
            "page": page_number,
            "chunk_id": chunk_id,
            "text": chunk_text
        })

        chunk_id += 1
        start = end - overlap

    return chunks

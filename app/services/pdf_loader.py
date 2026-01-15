import base64
from io import BytesIO
from typing import List, Dict
from pypdf import PdfReader


def pdf_to_pages(pdf_bytes: bytes) -> List[Dict]:
    
    # Convert PDF bytes -> Base64 -> decode -> extract text page-wise
    # Returns a list of {page, text}
    # 1. Encode to Base64
    encoded_pdf = base64.b64encode(pdf_bytes)

    # 2. Decode back to bytes
    decoded_pdf = base64.b64decode(encoded_pdf)

    # 3. Load PDF from memory
    pdf_stream = BytesIO(decoded_pdf)
    reader = PdfReader(pdf_stream)

    pages = []

    # 4. Extract text page by page
    for idx, page in enumerate(reader.pages):
        page_text = page.extract_text()
        if page_text:
            pages.append({
                "page": idx + 1,   # human-readable page number
                "text": page_text.strip()
            })

    return pages

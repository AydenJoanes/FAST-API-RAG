import os
import requests
from dotenv import load_dotenv
from app.core.logging import logger

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL_NAME = "mistralai/mistral-7b-instruct"


def call_llm(context: str, question: str) -> str:
    logger.debug(f"Calling LLM with question: {question[:50]}...")
    
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a document-grounded assistant.\n\n"
                    "Rules you MUST follow:\n"
                    "- Use ONLY the information present in the provided context.\n"
                    "- Do NOT use any external knowledge.\n"
                    "- Do NOT make assumptions or guesses.\n"
                    "- If the answer is not present in the context, say:\n"
                    "  \"The document does not contain this information.\"\n"
                    "- Be concise and clear.\n"
                    "- Summarize information instead of copying raw text.\n"
                    "- Do NOT include IDs, reference numbers, GSTIN, CIN, signatures, "
                    "or contact details unless explicitly asked.\n"
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Context:\n{context}\n\n"
                    f"Question:\n{question}\n\n"
                    "Answer:"
                ),
            },
        ],
    }

    try:
        response = requests.post(OPENROUTER_URL, headers=headers, json=payload)
        response.raise_for_status()
        answer = response.json()["choices"][0]["message"]["content"]
        logger.info(f"LLM response received ({len(answer)} chars)")
        return answer
    except Exception as e:
        logger.error(f"LLM call failed: {e}")
        raise

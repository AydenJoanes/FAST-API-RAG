"""Services package for rag_fastapi.

Note: Most services have been migrated to infrastructure/ layer:
- Embeddings -> infrastructure/embedders/
- Vector Store -> infrastructure/persistence/
- Document Loaders -> infrastructure/document_loaders/
- Chunkers -> infrastructure/chunkers/
- LLM Providers -> infrastructure/llm_providers/

Remaining in services/:
- tag_inference: Business logic for tag inference
"""

__all__ = ["tag_inference"]

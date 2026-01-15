"""
Application Services - Service Layer + Facade Pattern

This package contains application services that orchestrate
infrastructure components and encapsulate business logic.

Design Patterns:
- Facade: Services provide simplified interface to complex subsystems
- Dependency Injection: Services receive dependencies through constructor

SOLID Principles:
- SRP: Each service handles one domain concern
- DIP: Services depend on abstractions (interfaces)
"""
from .ingest_service import IngestService
from .chat_service import ChatService
from .retrieval_service import RetrievalService

__all__ = ["IngestService", "ChatService", "RetrievalService"]

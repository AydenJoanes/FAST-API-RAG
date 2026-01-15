"""LLM Provider Adapters - Adapter Pattern Implementation"""
from .openrouter_adapter import OpenRouterAdapter, get_llm_provider

__all__ = ["OpenRouterAdapter", "get_llm_provider"]

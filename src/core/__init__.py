"""Core modules for the Legal Document Analyzer."""

from .parser import document_parser, parse_document, parse_and_store_document
from .llm_manager import llm_manager, invoke_llm, batch_invoke_llm, get_llm_status, switch_llm_provider
from .agent import legal_agent, analyze_document, analyze_and_store_document

__all__ = [
    "document_parser", "parse_document", "parse_and_store_document",
    "llm_manager", "invoke_llm", "batch_invoke_llm", "get_llm_status", "switch_llm_provider",
    "legal_agent", "analyze_document", "analyze_and_store_document"
]

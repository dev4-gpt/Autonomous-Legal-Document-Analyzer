"""Database module for the Legal Document Analyzer."""

from .database import db_manager, get_db, init_database, reset_database, with_db_session
from .models import (
    Document, Analysis, Clause, RiskAssessment, UserSession, 
    ProcessingQueue, SystemMetrics, get_document_stats, 
    get_recent_activity, cleanup_old_sessions
)

__all__ = [
    "db_manager", "get_db", "init_database", "reset_database", "with_db_session",
    "Document", "Analysis", "Clause", "RiskAssessment", "UserSession",
    "ProcessingQueue", "SystemMetrics", "get_document_stats",
    "get_recent_activity", "cleanup_old_sessions"
]

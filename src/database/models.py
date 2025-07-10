"""
Database models for the Legal Document Analyzer.
SQLAlchemy models for storing analysis results, user sessions, and metadata.
"""

from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Float, Boolean,
    JSON, ForeignKey, Index, UniqueConstraint
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Session
from sqlalchemy.sql import func

Base = declarative_base()


class Document(Base):
    """Model for storing document metadata and basic information."""
    
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    doc_id = Column(String(255), unique=True, index=True, nullable=False)
    filename = Column(String(500), nullable=False)
    file_path = Column(String(1000), nullable=False)
    file_size = Column(Integer, nullable=False)
    file_type = Column(String(50), nullable=False)
    upload_timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    processed_timestamp = Column(DateTime, nullable=True)
    processing_status = Column(String(50), default="pending", nullable=False)  # pending, processing, completed, failed
    processing_time = Column(Float, nullable=True)  # in seconds
    error_message = Column(Text, nullable=True)
    
    # Relationships
    analysis = relationship("Analysis", back_populates="document", uselist=False)
    clauses = relationship("Clause", back_populates="document")
    risks = relationship("RiskAssessment", back_populates="document")
    
    def __repr__(self):
        return f"<Document(doc_id='{self.doc_id}', filename='{self.filename}')>"


class Analysis(Base):
    """Model for storing complete document analysis results."""
    
    __tablename__ = "analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    contract_type = Column(String(100), nullable=True)
    summary = Column(Text, nullable=True)
    overall_risk_level = Column(String(50), nullable=True)
    confidence_score = Column(Float, nullable=True)  # 0.0 to 1.0
    analysis_timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    llm_provider = Column(String(50), nullable=False)
    llm_model = Column(String(100), nullable=False)
    processing_metadata = Column(JSON, nullable=True)  # Store additional processing info
    
    # Relationships
    document = relationship("Document", back_populates="analysis")
    
    def __repr__(self):
        return f"<Analysis(document_id={self.document_id}, contract_type='{self.contract_type}')>"


class Clause(Base):
    """Model for storing extracted clauses from documents."""
    
    __tablename__ = "clauses"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    clause_type = Column(String(100), nullable=False, index=True)
    clause_text = Column(Text, nullable=False)
    start_position = Column(Integer, nullable=True)  # Character position in document
    end_position = Column(Integer, nullable=True)
    confidence_score = Column(Float, nullable=True)
    extraction_timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    document = relationship("Document", back_populates="clauses")
    risk_assessment = relationship("RiskAssessment", back_populates="clause", uselist=False)
    
    # Indexes
    __table_args__ = (
        Index('idx_document_clause_type', 'document_id', 'clause_type'),
    )
    
    def __repr__(self):
        return f"<Clause(document_id={self.document_id}, type='{self.clause_type}')>"


class RiskAssessment(Base):
    """Model for storing risk assessments of clauses."""
    
    __tablename__ = "risk_assessments"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    clause_id = Column(Integer, ForeignKey("clauses.id"), nullable=False)
    risk_level = Column(String(50), nullable=False, index=True)  # Low, Medium, High, Critical
    risk_score = Column(Float, nullable=True)  # 0.0 to 1.0
    rationale = Column(Text, nullable=True)
    factors = Column(JSON, nullable=True)  # Store risk factors as JSON
    assessment_timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    document = relationship("Document", back_populates="risks")
    clause = relationship("Clause", back_populates="risk_assessment")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('document_id', 'clause_id', name='uq_document_clause_risk'),
        Index('idx_risk_level', 'risk_level'),
    )
    
    def __repr__(self):
        return f"<RiskAssessment(document_id={self.document_id}, risk_level='{self.risk_level}')>"


class UserSession(Base):
    """Model for tracking user sessions and activity."""
    
    __tablename__ = "user_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), unique=True, index=True, nullable=False)
    user_identifier = Column(String(255), nullable=True)  # IP address or user ID
    start_timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_activity = Column(DateTime, default=datetime.utcnow, nullable=False)
    documents_processed = Column(Integer, default=0, nullable=False)
    session_data = Column(JSON, nullable=True)  # Store session preferences
    is_active = Column(Boolean, default=True, nullable=False)
    
    def __repr__(self):
        return f"<UserSession(session_id='{self.session_id}', active={self.is_active})>"


class ProcessingQueue(Base):
    """Model for managing document processing queue."""
    
    __tablename__ = "processing_queue"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    priority = Column(Integer, default=0, nullable=False)  # Higher number = higher priority
    status = Column(String(50), default="queued", nullable=False)  # queued, processing, completed, failed
    created_timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    started_timestamp = Column(DateTime, nullable=True)
    completed_timestamp = Column(DateTime, nullable=True)
    worker_id = Column(String(100), nullable=True)
    retry_count = Column(Integer, default=0, nullable=False)
    error_message = Column(Text, nullable=True)
    
    # Indexes
    __table_args__ = (
        Index('idx_queue_status_priority', 'status', 'priority'),
        Index('idx_queue_created', 'created_timestamp'),
    )
    
    def __repr__(self):
        return f"<ProcessingQueue(document_id={self.document_id}, status='{self.status}')>"


class SystemMetrics(Base):
    """Model for storing system performance metrics."""
    
    __tablename__ = "system_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    metric_name = Column(String(100), nullable=False, index=True)
    metric_value = Column(Float, nullable=False)
    metric_unit = Column(String(50), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    metadata = Column(JSON, nullable=True)
    
    # Indexes
    __table_args__ = (
        Index('idx_metrics_name_timestamp', 'metric_name', 'timestamp'),
    )
    
    def __repr__(self):
        return f"<SystemMetrics(name='{self.metric_name}', value={self.metric_value})>"


# Database utility functions
def get_document_stats(db: Session) -> Dict[str, Any]:
    """Get comprehensive document processing statistics."""
    total_docs = db.query(Document).count()
    processed_docs = db.query(Document).filter(Document.processing_status == "completed").count()
    failed_docs = db.query(Document).filter(Document.processing_status == "failed").count()
    
    # Average processing time
    avg_processing_time = db.query(func.avg(Document.processing_time)).filter(
        Document.processing_time.isnot(None)
    ).scalar() or 0
    
    # Risk distribution
    risk_distribution = db.query(
        RiskAssessment.risk_level,
        func.count(RiskAssessment.id)
    ).group_by(RiskAssessment.risk_level).all()
    
    # Contract type distribution
    contract_types = db.query(
        Analysis.contract_type,
        func.count(Analysis.id)
    ).group_by(Analysis.contract_type).all()
    
    return {
        "total_documents": total_docs,
        "processed_documents": processed_docs,
        "failed_documents": failed_docs,
        "success_rate": (processed_docs / total_docs * 100) if total_docs > 0 else 0,
        "average_processing_time": round(avg_processing_time, 2),
        "risk_distribution": dict(risk_distribution),
        "contract_types": dict(contract_types)
    }


def get_recent_activity(db: Session, limit: int = 10) -> List[Document]:
    """Get recently processed documents."""
    return db.query(Document).filter(
        Document.processing_status == "completed"
    ).order_by(Document.processed_timestamp.desc()).limit(limit).all()


def cleanup_old_sessions(db: Session, days: int = 7):
    """Clean up old inactive sessions."""
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    db.query(UserSession).filter(
        UserSession.last_activity < cutoff_date
    ).delete()
    db.commit()

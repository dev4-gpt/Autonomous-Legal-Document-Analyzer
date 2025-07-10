"""
Configuration settings for the Legal Document Analyzer.
Centralized configuration management with environment variable support.
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

class Config:
    """Main configuration class with environment-based settings."""
    
    # Base paths
    BASE_DIR = Path(__file__).parent.parent.parent
    DATA_DIR = BASE_DIR / "data"
    UPLOADS_DIR = DATA_DIR / "uploads"
    ANALYSIS_DIR = DATA_DIR / "analysis"
    VECTORSTORE_DIR = DATA_DIR / "vectorstore"
    LOGS_DIR = BASE_DIR / "logs"
    
    # Database settings
    DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DATA_DIR}/legal_analyzer.db")
    
    # LLM Configuration
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama").lower()
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-3-opus-20240229")
    
    # Vector Store Configuration
    VECTOR_DB_TYPE = os.getenv("VECTOR_DB_TYPE", "faiss")  # faiss or chroma
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))
    
    # Processing Configuration
    MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "50"))
    SUPPORTED_EXTENSIONS = [".pdf", ".docx", ".txt", ".html"]
    BATCH_SIZE = int(os.getenv("BATCH_SIZE", "10"))
    
    # UI Configuration
    APP_TITLE = os.getenv("APP_TITLE", "Autonomous Legal Document Analyzer")
    APP_DESCRIPTION = os.getenv("APP_DESCRIPTION", "Enterprise AI-powered legal document analysis")
    THEME = os.getenv("THEME", "dark")
    
    # Security Configuration
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    SESSION_TIMEOUT = int(os.getenv("SESSION_TIMEOUT", "3600"))  # 1 hour
    
    # Logging Configuration
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Performance Configuration
    MAX_WORKERS = int(os.getenv("MAX_WORKERS", "4"))
    CACHE_TTL = int(os.getenv("CACHE_TTL", "3600"))  # 1 hour
    
    # Legal Analysis Configuration
    DEFAULT_CLAUSES = [
        "Termination", "Indemnity", "Confidentiality", "Liability", 
        "Intellectual Property", "Payment Terms", "Governing Law",
        "Force Majeure", "Dispute Resolution", "Data Protection"
    ]
    
    RISK_LEVELS = ["Low", "Medium", "High", "Critical"]
    CONTRACT_TYPES = ["NDA", "SLA", "MSA", "Employment", "License", "Other"]
    
    @classmethod
    def create_directories(cls):
        """Create necessary directories if they don't exist."""
        directories = [
            cls.DATA_DIR, cls.UPLOADS_DIR, cls.ANALYSIS_DIR,
            cls.VECTORSTORE_DIR, cls.LOGS_DIR
        ]
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def validate_config(cls) -> Dict[str, Any]:
        """Validate configuration and return status."""
        issues = []
        
        # Check LLM configuration
        if cls.LLM_PROVIDER == "openai" and not cls.OPENAI_API_KEY:
            issues.append("OpenAI API key not configured")
        elif cls.LLM_PROVIDER == "anthropic" and not cls.ANTHROPIC_API_KEY:
            issues.append("Anthropic API key not configured")
        
        # Check file size limits
        if cls.MAX_FILE_SIZE_MB <= 0:
            issues.append("Invalid max file size configuration")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "provider": cls.LLM_PROVIDER,
            "vector_db": cls.VECTOR_DB_TYPE
        }

class DevelopmentConfig(Config):
    """Development environment configuration."""
    DEBUG = True
    LOG_LEVEL = "DEBUG"

class ProductionConfig(Config):
    """Production environment configuration."""
    DEBUG = False
    LOG_LEVEL = "WARNING"

class TestingConfig(Config):
    """Testing environment configuration."""
    DEBUG = True
    LOG_LEVEL = "DEBUG"
    DATABASE_URL = "sqlite:///:memory:"

# Configuration factory
def get_config() -> Config:
    """Get configuration based on environment."""
    env = os.getenv("ENVIRONMENT", "development").lower()
    
    if env == "production":
        return ProductionConfig()
    elif env == "testing":
        return TestingConfig()
    else:
        return DevelopmentConfig()

# Global config instance
config = get_config()

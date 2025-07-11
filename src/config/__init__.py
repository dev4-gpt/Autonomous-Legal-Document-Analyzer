"""Configuration module for the Legal Document Analyzer."""

from .settings import config, Config, get_config

class TestingConfig:
    ENVIRONMENT = "test"
    DATABASE_URL = "sqlite:///data/test_legal_analyzer.db"
    # Add other required test config variables here
    MAX_FILE_SIZE_MB = 5
    BATCH_SIZE = 2
    MAX_WORKERS = 1
    SECRET_KEY = "test-secret"
    VECTOR_DB_TYPE = "faiss"
    EMBEDDING_MODEL = "all-MiniLM-L6-v2"

__all__ = ["config", "Config", "get_config", "TestingConfig"]

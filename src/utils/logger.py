"""
Comprehensive logging system for the Legal Document Analyzer.
Provides structured logging with different levels and output formats.
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime

from src.config import config


class ColoredFormatter(logging.Formatter):
    """Custom formatter with color support for console output."""
    
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
        'RESET': '\033[0m'      # Reset
    }
    
    def format(self, record):
        if hasattr(record, 'levelname'):
            color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
            record.levelname = f"{color}{record.levelname}{self.COLORS['RESET']}"
        return super().format(record)


class LegalAnalyzerLogger:
    """Main logger class for the application."""
    
    def __init__(self, name: str = "legal_analyzer"):
        self.name = name
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, config.LOG_LEVEL))
        
        # Prevent duplicate handlers
        if not self.logger.handlers:
            self._setup_handlers()
    
    def _setup_handlers(self):
        """Set up console and file handlers."""
        # Console handler with colors
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)
        console_formatter = ColoredFormatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        
        # File handler for general logs
        config.LOGS_DIR.mkdir(parents=True, exist_ok=True)
        file_handler = logging.handlers.RotatingFileHandler(
            config.LOGS_DIR / "legal_analyzer.log",
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(logging.INFO)
        file_formatter = logging.Formatter(config.LOG_FORMAT)
        file_handler.setFormatter(file_formatter)
        
        # Error file handler
        error_handler = logging.handlers.RotatingFileHandler(
            config.LOGS_DIR / "errors.log",
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(file_formatter)
        
        # Add handlers to logger
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)
        self.logger.addHandler(error_handler)
    
    def debug(self, message: str, **kwargs):
        """Log debug message."""
        self.logger.debug(message, extra=kwargs)
    
    def info(self, message: str, **kwargs):
        """Log info message."""
        self.logger.info(message, extra=kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message."""
        self.logger.warning(message, extra=kwargs)
    
    def error(self, message: str, exception: Optional[Exception] = None, **kwargs):
        """Log error message with optional exception."""
        if exception:
            self.logger.error(f"{message}: {str(exception)}", exc_info=True, extra=kwargs)
        else:
            self.logger.error(message, extra=kwargs)
    
    def critical(self, message: str, exception: Optional[Exception] = None, **kwargs):
        """Log critical message with optional exception."""
        if exception:
            self.logger.critical(f"{message}: {str(exception)}", exc_info=True, extra=kwargs)
        else:
            self.logger.critical(message, extra=kwargs)


class AnalysisLogger(LegalAnalyzerLogger):
    """Specialized logger for document analysis operations."""
    
    def __init__(self):
        super().__init__("analysis")
        
        # Add analysis-specific file handler
        analysis_handler = logging.handlers.RotatingFileHandler(
            config.LOGS_DIR / "analysis.log",
            maxBytes=10*1024*1024,  # 10MB
            backupCount=10
        )
        analysis_handler.setLevel(logging.INFO)
        analysis_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - [%(funcName)s] - %(message)s'
        )
        analysis_handler.setFormatter(analysis_formatter)
        self.logger.addHandler(analysis_handler)
    
    def log_document_processed(self, doc_id: str, processing_time: float, success: bool):
        """Log document processing completion."""
        status = "SUCCESS" if success else "FAILED"
        self.info(f"Document {doc_id} processed - Status: {status}, Time: {processing_time:.2f}s")
    
    def log_analysis_start(self, doc_id: str, file_size: int):
        """Log analysis start."""
        self.info(f"Starting analysis for {doc_id} (Size: {file_size} bytes)")
    
    def log_clause_extraction(self, doc_id: str, clause_count: int):
        """Log clause extraction results."""
        self.info(f"Extracted {clause_count} clauses from {doc_id}")
    
    def log_risk_assessment(self, doc_id: str, risk_distribution: dict):
        """Log risk assessment results."""
        self.info(f"Risk assessment for {doc_id}: {risk_distribution}")


class PerformanceLogger(LegalAnalyzerLogger):
    """Logger for performance monitoring."""
    
    def __init__(self):
        super().__init__("performance")
        
        # Add performance-specific file handler
        perf_handler = logging.handlers.RotatingFileHandler(
            config.LOGS_DIR / "performance.log",
            maxBytes=5*1024*1024,  # 5MB
            backupCount=5
        )
        perf_handler.setLevel(logging.INFO)
        perf_formatter = logging.Formatter(
            '%(asctime)s - %(message)s'
        )
        perf_handler.setFormatter(perf_formatter)
        self.logger.addHandler(perf_handler)
    
    def log_timing(self, operation: str, duration: float, **metadata):
        """Log operation timing."""
        metadata_str = ", ".join([f"{k}={v}" for k, v in metadata.items()])
        self.info(f"TIMING - {operation}: {duration:.3f}s - {metadata_str}")
    
    def log_memory_usage(self, operation: str, memory_mb: float):
        """Log memory usage."""
        self.info(f"MEMORY - {operation}: {memory_mb:.2f}MB")


# Global logger instances
logger = LegalAnalyzerLogger()
analysis_logger = AnalysisLogger()
performance_logger = PerformanceLogger()

# Convenience functions
def get_logger(name: str = "legal_analyzer") -> LegalAnalyzerLogger:
    """Get a logger instance."""
    return LegalAnalyzerLogger(name)

def log_startup():
    """Log application startup information."""
    logger.info("=" * 60)
    logger.info("Legal Document Analyzer Starting Up")
    logger.info(f"Version: 2.0.0")
    logger.info(f"Environment: {config.LLM_PROVIDER}")
    logger.info(f"Log Level: {config.LOG_LEVEL}")
    logger.info(f"Data Directory: {config.DATA_DIR}")
    logger.info("=" * 60)

def log_shutdown():
    """Log application shutdown."""
    logger.info("Legal Document Analyzer Shutting Down")
    logger.info("=" * 60)

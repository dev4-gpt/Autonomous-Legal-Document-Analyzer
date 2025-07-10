"""
Main application entry point for the Legal Document Analyzer.
Enhanced enterprise-grade legal document analysis system.
"""

import sys
import os
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Import and run the main application
from src.ui import main

if __name__ == "__main__":
    main()

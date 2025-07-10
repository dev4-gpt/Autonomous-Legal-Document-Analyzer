"""
Setup script for the Legal Document Analyzer.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

# Read requirements
requirements = []
with open("requirements.txt", "r") as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="legal-document-analyzer",
    version="2.0.0",
    author="Legal AI Systems",
    author_email="contact@legalai.systems",
    description="Enterprise-grade autonomous legal document analyzer",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dev4-gpt/Autonomous-Legal-Document-Analyzer",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Legal Industry",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Office/Business :: Legal",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Text Processing :: Linguistic",
    ],
    python_requires=">=3.11",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.1.0",
            "black>=23.9.0",
            "flake8>=6.1.0",
            "mypy>=1.6.0",
            "pre-commit>=3.5.0",
        ],
        "docs": [
            "sphinx>=7.2.0",
            "sphinx-rtd-theme>=1.3.0",
            "myst-parser>=2.0.0",
        ],
        "postgres": [
            "psycopg2-binary>=2.9.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "legal-analyzer=src.ui.main_app:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.txt", "*.md", "*.yml", "*.yaml"],
    },
    project_urls={
        "Bug Reports": "https://github.com/dev4-gpt/Autonomous-Legal-Document-Analyzer/issues",
        "Source": "https://github.com/dev4-gpt/Autonomous-Legal-Document-Analyzer",
        "Documentation": "https://github.com/dev4-gpt/Autonomous-Legal-Document-Analyzer/wiki",
    },
)

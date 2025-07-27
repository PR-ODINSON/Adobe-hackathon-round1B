"""
Persona-Driven Document Intelligence Pipeline

A sophisticated document processing system that extracts and ranks
relevant sections from PDF documents based on user persona and job requirements.

Main Components:
- parser: PDF text extraction and section identification
- embeddings: Text embedding generation using sentence-transformers
- matcher: Section ranking and relevance matching
- utils: Utility functions for JSON I/O and text processing
- main: Pipeline orchestration and execution

Usage:
    from src.main import DocumentIntelligencePipeline
    
    pipeline = DocumentIntelligencePipeline()
    results = pipeline.run()
"""

__version__ = "1.0.0"
__author__ = "Adobe Hackathon Team"
__email__ = "hackathon@adobe.com"

# Import main classes for easy access
from .main import DocumentIntelligencePipeline
from .parser import PDFParser, parse_document
from .embeddings import EmbeddingGenerator, create_embeddings
from .matcher import SectionMatcher, match_and_rank_sections

__all__ = [
    'DocumentIntelligencePipeline',
    'PDFParser', 
    'parse_document',
    'EmbeddingGenerator',
    'create_embeddings', 
    'SectionMatcher',
    'match_and_rank_sections'
] 
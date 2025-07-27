# Approach Explanation: Persona-Driven Document Intelligence

## Overview

This solution implements a sophisticated document intelligence pipeline that extracts the most relevant sections from PDF documents based on a given persona and job-to-be-done. The approach combines traditional PDF parsing with modern semantic similarity techniques to deliver contextually relevant information.

## Architecture

The system follows a modular pipeline architecture with five core components:

1. **PDF Parser** (`parser.py`): Extracts text and identifies document structure using PyMuPDF
2. **Embedding Generator** (`embeddings.py`): Creates semantic vector representations using sentence-transformers
3. **Section Matcher** (`matcher.py`): Ranks document sections by relevance using cosine similarity
4. **Utilities** (`utils.py`): Provides text processing, validation, and I/O functions
5. **Main Pipeline** (`main.py`): Orchestrates the entire workflow with robust error handling

## Document Structure Detection

The PDF parser employs multiple heuristics to identify section headings and document structure:

- **Font-based detection**: Analyzes text size, weight, and formatting differences
- **Position-based analysis**: Considers line spacing, indentation, and page positioning
- **Content-based patterns**: Uses regex patterns to detect common heading formats (numbered sections, capitalized text)
- **Context awareness**: Filters out false positives using content length and surrounding text analysis

## Semantic Embedding Strategy

The system uses the `all-MiniLM-L6-v2` model from sentence-transformers for generating embeddings because:

- **Balanced performance**: Offers good quality embeddings with reasonable computational requirements
- **Offline capability**: Can be cached locally for Docker deployment without internet dependency
- **Multilingual support**: Handles diverse document types and technical content effectively

Text chunking is applied to large sections using overlapping windows (default 512 tokens with 64-token overlap) to preserve context while maintaining embedding quality.

## Ranking and Relevance

The matching algorithm combines persona and job-to-be-done into a structured query prompt: "As a [persona], I need to [job_to_be_done]. Help me find relevant information." This approach:

- **Contextualizes the search**: Ensures relevance to both role and task
- **Improves semantic matching**: Creates richer query representations than simple keyword matching
- **Maintains interpretability**: Results can be traced back to specific similarity scores

Cosine similarity is used for ranking because it's invariant to document length and provides intuitive relevance scores between 0 and 1.

## Robustness Features

The pipeline includes comprehensive error handling:

- **Auto-discovery**: Automatically finds all PDF files in the input directory
- **Graceful degradation**: Continues processing even if individual documents fail
- **Format validation**: Ensures input JSON contains required fields with proper types
- **Output consistency**: Maintains standardized JSON structure regardless of input quality

## Performance Considerations

The system is optimized for offline evaluation environments:

- **Batch processing**: Embeddings are generated in batches for efficiency
- **Memory management**: Large documents are chunked to prevent memory issues
- **Caching strategy**: Models are loaded once and reused throughout the pipeline
- **Minimal dependencies**: Uses only essential libraries to reduce deployment complexity

This approach provides a practical balance between accuracy, performance, and deployment simplicity for real-world document intelligence applications. 
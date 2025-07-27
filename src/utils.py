"""
Utility functions for document intelligence pipeline.
Handles JSON I/O, timestamps, and text formatting.
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any


def load_json(file_path: str) -> Dict[str, Any]:
    """Load JSON data from file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Input file not found: {file_path}")
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON format in {file_path}: {e}")


def save_json(data: Dict[str, Any], file_path: str) -> None:
    """Save data to JSON file with proper formatting."""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def get_timestamp() -> str:
    """Get current timestamp in ISO format."""
    return datetime.now().isoformat()


def clean_text(text: str) -> str:
    """Clean and normalize text content."""
    if not text:
        return ""
    
    # Remove excessive whitespace and normalize line breaks
    text = ' '.join(text.split())
    
    # Remove special characters that might interfere with processing
    text = text.replace('\u00a0', ' ')  # Non-breaking space
    text = text.replace('\u2028', ' ')  # Line separator
    text = text.replace('\u2029', ' ')  # Paragraph separator
    
    return text.strip()


def chunk_text(text: str, max_chunk_size: int = 512, overlap: int = 50) -> List[str]:
    """
    Split text into overlapping chunks for better embedding.
    
    Args:
        text: Input text to chunk
        max_chunk_size: Maximum number of characters per chunk
        overlap: Number of characters to overlap between chunks
    
    Returns:
        List of text chunks
    """
    if not text or len(text) <= max_chunk_size:
        return [text] if text else []
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + max_chunk_size
        
        # Try to break at word boundary
        if end < len(text):
            # Find the last space within the chunk
            last_space = text.rfind(' ', start, end)
            if last_space > start:
                end = last_space
        
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        
        # Move start position with overlap
        start = max(start + 1, end - overlap)
        
        # Prevent infinite loop
        if start >= len(text):
            break
    
    return chunks


def format_section_title(title: str) -> str:
    """Format section title for consistent display."""
    if not title:
        return "Untitled Section"
    
    # Clean the title
    title = clean_text(title)
    
    # Capitalize properly
    if title.isupper():
        title = title.title()
    
    return title


def validate_input_data(data: Dict[str, Any]) -> bool:
    """
    Validate input JSON structure.
    
    Expected structure:
    {
        "persona": "string",
        "job_to_be_done": "string", 
        "documents": ["path1", "path2", ...]
    }
    """
    required_fields = ["persona", "job_to_be_done", "documents"]
    
    for field in required_fields:
        if field not in data:
            raise ValueError(f"Missing required field: {field}")
    
    if not isinstance(data["documents"], list) or not data["documents"]:
        raise ValueError("Documents field must be a non-empty list")
    
    return True


def create_output_structure(metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Create the basic output structure with metadata."""
    return {
        "metadata": {
            "input_documents": metadata.get("documents", []),
            "persona": metadata.get("persona", ""),
            "job_to_be_done": metadata.get("job_to_be_done", ""),
            "processing_timestamp": get_timestamp()
        },
        "extracted_sections": [],
        "subsection_analysis": []
    } 
"""
Matcher module for ranking and selecting relevant document sections.
Uses semantic similarity and relevance scoring to match sections with persona/job requirements.
"""

import numpy as np
from typing import List, Dict, Any, Tuple
from sklearn.metrics.pairwise import cosine_similarity


def match_and_rank_sections(query_embedding: np.ndarray, 
                           embedded_sections: List[Dict[str, Any]], 
                           top_k: int = 10) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Match and rank document sections based on semantic similarity with query.
    
    Args:
        query_embedding: Embedding vector for the combined persona + job query
        embedded_sections: List of sections with their embeddings
        top_k: Number of top sections to return
    
    Returns:
        Tuple of (extracted_sections, subsection_analysis) in hackathon format
    """
    if not embedded_sections:
        return [], []
    
    # Extract embeddings from sections
    section_embeddings = np.array([section['embedding'] for section in embedded_sections])
    
    # Calculate cosine similarities
    similarities = cosine_similarity([query_embedding], section_embeddings)[0]
    
    # Create ranked results
    ranked_indices = np.argsort(similarities)[::-1]  # Sort in descending order
    top_indices = ranked_indices[:top_k]
    
    # Format extracted_sections (top-level summary)
    extracted_sections = []
    for i, idx in enumerate(top_indices[:5]):  # Top 5 for extracted_sections
        section = embedded_sections[idx]
        extracted_sections.append({
            "document": section['document'],
            "section_title": section['title'],
            "importance_rank": i + 1,
            "page_number": section['page_number']
        })
    
    # Format subsection_analysis (detailed content)
    subsection_analysis = []
    for idx in top_indices[:5]:  # Top 5 for detailed analysis
        section = embedded_sections[idx]
        subsection_analysis.append({
            "document": section['document'],
            "refined_text": section['content'][:500] + "..." if len(section['content']) > 500 else section['content'],
            "page_number": section['page_number']
        })
    
    return extracted_sections, subsection_analysis


def calculate_relevance_score(section: Dict[str, Any], persona: str, job_to_be_done: str) -> float:
    """
    Calculate relevance score for a section based on content analysis.
    
    Args:
        section: Section dictionary with title and content
        persona: User persona string
        job_to_be_done: Task description string
    
    Returns:
        Relevance score between 0 and 1
    """
    # Simple keyword-based scoring (can be enhanced with more sophisticated NLP)
    content = (section.get('title', '') + ' ' + section.get('content', '')).lower()
    query = (persona + ' ' + job_to_be_done).lower()
    
    # Extract keywords from query
    query_words = set(query.split())
    content_words = set(content.split())
    
    # Calculate overlap
    overlap = len(query_words.intersection(content_words))
    total_query_words = len(query_words)
    
    if total_query_words == 0:
        return 0.0
    
    return min(overlap / total_query_words, 1.0)


def filter_sections_by_relevance(sections: List[Dict[str, Any]], 
                                persona: str, 
                                job_to_be_done: str,
                                min_score: float = 0.1) -> List[Dict[str, Any]]:
    """
    Filter sections by minimum relevance score.
    
    Args:
        sections: List of section dictionaries
        persona: User persona string
        job_to_be_done: Task description string
        min_score: Minimum relevance score threshold
    
    Returns:
        Filtered list of relevant sections
    """
    relevant_sections = []
    
    for section in sections:
        score = calculate_relevance_score(section, persona, job_to_be_done)
        if score >= min_score:
            section['relevance_score'] = score
            relevant_sections.append(section)
    
    # Sort by relevance score
    relevant_sections.sort(key=lambda x: x['relevance_score'], reverse=True)
    
    return relevant_sections


def enhance_section_content(section: Dict[str, Any], persona: str, job_to_be_done: str) -> str:
    """
    Enhance section content by highlighting relevant parts.
    
    Args:
        section: Section dictionary
        persona: User persona string
        job_to_be_done: Task description string
    
    Returns:
        Enhanced content string
    """
    content = section.get('content', '')
    
    # For now, return original content
    # This can be enhanced with summarization or highlighting
    return content 
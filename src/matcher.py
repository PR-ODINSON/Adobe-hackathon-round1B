"""
Section matching and ranking module.
Matches document sections to user queries based on embedding similarity.
"""

import numpy as np
from typing import List, Dict, Any, Tuple
from .embeddings import calculate_cosine_similarity


class SectionMatcher:
    """Handles matching and ranking of document sections based on relevance."""
    
    def __init__(self, min_similarity_threshold: float = 0.3):
        """
        Initialize the matcher.
        
        Args:
            min_similarity_threshold: Minimum similarity score to consider a section relevant
        """
        self.min_similarity_threshold = min_similarity_threshold
    
    def rank_sections(self, query_embedding: np.ndarray, 
                     embedded_sections: List[Dict[str, Any]],
                     top_k: int = 10) -> List[Dict[str, Any]]:
        """
        Rank sections by relevance to the query.
        
        Args:
            query_embedding: Embedding vector for the user query
            embedded_sections: List of sections with embeddings
            top_k: Number of top sections to return
        
        Returns:
            List of ranked sections with similarity scores
        """
        scored_sections = []
        
        for section in embedded_sections:
            if 'embedding' not in section:
                continue
            
            # Calculate similarity
            similarity = calculate_cosine_similarity(
                query_embedding, 
                section['embedding']
            )
            
            # Only include sections above threshold
            if similarity >= self.min_similarity_threshold:
                section_copy = section.copy()
                section_copy['similarity_score'] = float(similarity)
                scored_sections.append(section_copy)
        
        # Sort by similarity score (descending)
        scored_sections.sort(key=lambda x: x['similarity_score'], reverse=True)
        
        # Return top k results
        return scored_sections[:top_k]
    
    def group_sections_by_document(self, ranked_sections: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Group ranked sections by source document.
        
        Args:
            ranked_sections: List of ranked sections
        
        Returns:
            Dictionary mapping document names to their ranked sections
        """
        grouped = {}
        
        for section in ranked_sections:
            doc_name = section.get('document', 'unknown')
            
            if doc_name not in grouped:
                grouped[doc_name] = []
            
            grouped[doc_name].append(section)
        
        return grouped
    
    def merge_chunked_sections(self, ranked_sections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Merge chunked sections from the same original section.
        
        Args:
            ranked_sections: List of ranked sections (may include chunks)
        
        Returns:
            List of merged sections
        """
        # Group by original section (document + title + page)
        section_groups = {}
        
        for section in ranked_sections:
            key = (
                section.get('document', ''),
                section.get('title', ''),
                section.get('page_number', 0)
            )
            
            if key not in section_groups:
                section_groups[key] = []
            
            section_groups[key].append(section)
        
        merged_sections = []
        
        for key, sections in section_groups.items():
            if len(sections) == 1:
                # Single section or single chunk
                merged_sections.append(sections[0])
            else:
                # Multiple chunks from same section - merge them
                merged_section = self._merge_section_chunks(sections)
                merged_sections.append(merged_section)
        
        # Re-sort by best similarity score
        merged_sections.sort(key=lambda x: x['similarity_score'], reverse=True)
        
        return merged_sections
    
    def _merge_section_chunks(self, chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Merge multiple chunks from the same section.
        
        Args:
            chunks: List of chunk sections to merge
        
        Returns:
            Merged section dictionary
        """
        if not chunks:
            return {}
        
        # Use the chunk with highest similarity as base
        best_chunk = max(chunks, key=lambda x: x.get('similarity_score', 0))
        
        merged = best_chunk.copy()
        
        # Merge content from all chunks
        all_chunk_texts = []
        for chunk in sorted(chunks, key=lambda x: x.get('chunk_id', 0)):
            chunk_text = chunk.get('chunk_text', chunk.get('content', ''))
            if chunk_text:
                all_chunk_texts.append(chunk_text)
        
        # Combine content
        merged['content'] = ' '.join(all_chunk_texts)
        merged['merged_chunks'] = len(chunks)
        merged['chunk_similarities'] = [chunk.get('similarity_score', 0) for chunk in chunks]
        
        # Remove chunk-specific fields
        for field in ['chunk_id', 'chunk_text', 'is_chunked', 'total_chunks']:
            merged.pop(field, None)
        
        return merged
    
    def create_section_summaries(self, ranked_sections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Create summary information for ranked sections.
        
        Args:
            ranked_sections: List of ranked sections
        
        Returns:
            List of section summaries for output
        """
        summaries = []
        
        for i, section in enumerate(ranked_sections):
            summary = {
                "document": section.get('document', 'unknown'),
                "section_title": section.get('title', 'Untitled'),
                "importance_rank": i + 1,
                "page_number": section.get('page_number', 0),
                "similarity_score": round(section.get('similarity_score', 0), 4)
            }
            
            summaries.append(summary)
        
        return summaries
    
    def create_subsection_analysis(self, ranked_sections: List[Dict[str, Any]], 
                                  max_subsections: int = 5) -> List[Dict[str, Any]]:
        """
        Create detailed subsection analysis for top sections.
        
        Args:
            ranked_sections: List of ranked sections
            max_subsections: Maximum number of subsections to analyze
        
        Returns:
            List of subsection analysis entries
        """
        analysis = []
        
        for section in ranked_sections[:max_subsections]:
            content = section.get('content', '')
            
            # Create refined text (first 500 characters with proper sentence ending)
            refined_text = self._create_refined_text(content)
            
            analysis_entry = {
                "document": section.get('document', 'unknown'),
                "section_title": section.get('title', 'Untitled'),
                "refined_text": refined_text,
                "page_number": section.get('page_number', 0),
                "similarity_score": round(section.get('similarity_score', 0), 4)
            }
            
            analysis.append(analysis_entry)
        
        return analysis
    
    def _create_refined_text(self, content: str, max_length: int = 500) -> str:
        """
        Create a refined version of the text for analysis output.
        
        Args:
            content: Original content text
            max_length: Maximum length of refined text
        
        Returns:
            Refined text summary
        """
        if not content:
            return "No content available."
        
        content = content.strip()
        
        if len(content) <= max_length:
            return content
        
        # Try to cut at sentence boundary
        truncated = content[:max_length]
        
        # Find last sentence ending
        last_period = truncated.rfind('.')
        last_exclamation = truncated.rfind('!')
        last_question = truncated.rfind('?')
        
        last_sentence_end = max(last_period, last_exclamation, last_question)
        
        if last_sentence_end > max_length * 0.7:  # If we can keep most of the text
            return truncated[:last_sentence_end + 1]
        else:
            # Cut at word boundary and add ellipsis
            last_space = truncated.rfind(' ')
            if last_space > 0:
                return truncated[:last_space] + "..."
            else:
                return truncated + "..."


def match_and_rank_sections(query_embedding: np.ndarray,
                           embedded_sections: List[Dict[str, Any]],
                           top_k: int = 10) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Main function to match and rank sections for a query.
    
    Args:
        query_embedding: Embedding vector for the user query
        embedded_sections: List of sections with embeddings
        top_k: Number of top sections to return
    
    Returns:
        Tuple of (section_summaries, subsection_analysis)
    """
    matcher = SectionMatcher()
    
    # Rank sections by similarity
    ranked_sections = matcher.rank_sections(query_embedding, embedded_sections, top_k)
    
    # Merge chunked sections if needed
    merged_sections = matcher.merge_chunked_sections(ranked_sections)
    
    # Create output summaries
    section_summaries = matcher.create_section_summaries(merged_sections)
    subsection_analysis = matcher.create_subsection_analysis(merged_sections)
    
    return section_summaries, subsection_analysis 
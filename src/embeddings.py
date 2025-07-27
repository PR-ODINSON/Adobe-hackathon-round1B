"""
Text embedding module using sentence-transformers.
Generates vector embeddings for persona/job descriptions and document sections.
"""

import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any, Tuple
from .utils import clean_text, chunk_text


class EmbeddingGenerator:
    """Handles text embedding generation using sentence-transformers."""
    
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        """
        Initialize the embedding generator.
        
        Args:
            model_name: Name of the sentence-transformer model to use
                       'all-MiniLM-L6-v2' is a good balance of speed and quality
        """
        try:
            self.model = SentenceTransformer(model_name)
            self.model_name = model_name
        except Exception as e:
            print(f"Warning: Could not load model {model_name}, falling back to default")
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            self.model_name = 'all-MiniLM-L6-v2'
    
    def create_query_embedding(self, persona: str, job_to_be_done: str) -> np.ndarray:
        """
        Create embedding for the user query (persona + job to be done).
        
        Args:
            persona: Description of the user persona
            job_to_be_done: Description of the task/job
        
        Returns:
            numpy array representing the combined embedding
        """
        # Combine persona and job into a single query
        combined_query = self._combine_persona_and_job(persona, job_to_be_done)
        
        # Generate embedding
        embedding = self.model.encode([combined_query])
        return embedding[0]  # Return single embedding vector
    
    def _combine_persona_and_job(self, persona: str, job_to_be_done: str) -> str:
        """
        Intelligently combine persona and job descriptions.
        
        Args:
            persona: User persona description
            job_to_be_done: Task description
        
        Returns:
            Combined text optimized for similarity matching
        """
        persona_clean = clean_text(persona)
        job_clean = clean_text(job_to_be_done)
        
        # Create a structured combination that emphasizes the task context
        combined = f"User Profile: {persona_clean}. Task Objective: {job_clean}. Looking for relevant information to help with: {job_clean}"
        
        return combined
    
    def create_section_embeddings(self, sections: List[Dict[str, Any]], 
                                 use_chunking: bool = True) -> List[Dict[str, Any]]:
        """
        Create embeddings for document sections.
        
        Args:
            sections: List of section dictionaries from parser
            use_chunking: Whether to chunk long sections for better embeddings
        
        Returns:
            List of section dictionaries with added embedding information
        """
        embedded_sections = []
        
        for section in sections:
            title = section.get('title', '')
            content = section.get('content', '')
            
            # Combine title and content for embedding
            full_text = self._prepare_section_text(title, content)
            
            if use_chunking and len(full_text) > 512:
                # Create embeddings for chunks
                chunks = chunk_text(full_text, max_chunk_size=512, overlap=50)
                
                for i, chunk in enumerate(chunks):
                    if chunk.strip():  # Skip empty chunks
                        embedding = self.model.encode([chunk])[0]
                        
                        chunk_section = section.copy()
                        chunk_section['chunk_id'] = i
                        chunk_section['chunk_text'] = chunk
                        chunk_section['embedding'] = embedding
                        chunk_section['is_chunked'] = True
                        chunk_section['total_chunks'] = len(chunks)
                        
                        embedded_sections.append(chunk_section)
            else:
                # Create single embedding for the entire section
                if full_text.strip():  # Skip empty sections
                    embedding = self.model.encode([full_text])[0]
                    
                    section_copy = section.copy()
                    section_copy['full_text'] = full_text
                    section_copy['embedding'] = embedding
                    section_copy['is_chunked'] = False
                    
                    embedded_sections.append(section_copy)
        
        return embedded_sections
    
    def _prepare_section_text(self, title: str, content: str) -> str:
        """
        Prepare section text for embedding by combining title and content.
        
        Args:
            title: Section title
            content: Section content
        
        Returns:
            Combined text optimized for embedding
        """
        title_clean = clean_text(title)
        content_clean = clean_text(content)
        
        if title_clean and content_clean:
            # Weight the title more heavily by repeating it
            return f"{title_clean}. {title_clean}: {content_clean}"
        elif title_clean:
            return title_clean
        elif content_clean:
            return content_clean
        else:
            return ""
    
    def batch_embed_texts(self, texts: List[str]) -> np.ndarray:
        """
        Create embeddings for a batch of texts efficiently.
        
        Args:
            texts: List of text strings to embed
        
        Returns:
            numpy array of embeddings (one per text)
        """
        if not texts:
            return np.array([])
        
        # Filter out empty texts
        valid_texts = [text for text in texts if text.strip()]
        
        if not valid_texts:
            return np.array([])
        
        # Generate embeddings in batch for efficiency
        embeddings = self.model.encode(valid_texts, show_progress_bar=len(valid_texts) > 10)
        
        return embeddings
    
    def get_embedding_dimension(self) -> int:
        """Get the dimensionality of the embeddings."""
        return self.model.get_sentence_embedding_dimension()
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the loaded model."""
        return {
            "model_name": self.model_name,
            "embedding_dimension": self.get_embedding_dimension(),
            "max_seq_length": getattr(self.model, 'max_seq_length', 'Unknown')
        }


def calculate_cosine_similarity(embedding1: np.ndarray, embedding2: np.ndarray) -> float:
    """
    Calculate cosine similarity between two embeddings.
    
    Args:
        embedding1: First embedding vector
        embedding2: Second embedding vector
    
    Returns:
        Cosine similarity score (0 to 1)
    """
    # Normalize vectors
    norm1 = np.linalg.norm(embedding1)
    norm2 = np.linalg.norm(embedding2)
    
    if norm1 == 0 or norm2 == 0:
        return 0.0
    
    # Calculate cosine similarity
    similarity = np.dot(embedding1, embedding2) / (norm1 * norm2)
    
    # Ensure result is in [0, 1] range (convert from [-1, 1])
    return (similarity + 1) / 2


def create_embeddings(persona: str, job_to_be_done: str, 
                     sections: List[Dict[str, Any]]) -> Tuple[np.ndarray, List[Dict[str, Any]]]:
    """
    Main function to create embeddings for query and document sections.
    
    Args:
        persona: User persona description
        job_to_be_done: Task description
        sections: List of document sections
    
    Returns:
        Tuple of (query_embedding, embedded_sections)
    """
    generator = EmbeddingGenerator()
    
    # Create query embedding
    query_embedding = generator.create_query_embedding(persona, job_to_be_done)
    
    # Create section embeddings
    embedded_sections = generator.create_section_embeddings(sections)
    
    return query_embedding, embedded_sections 
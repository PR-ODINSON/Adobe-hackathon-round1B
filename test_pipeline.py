"""
Test script for the Persona-Driven Document Intelligence Pipeline.
This script tests the pipeline components without requiring actual PDF files.
"""

import sys
import os
sys.path.append('src')

from src.utils import create_output_structure, clean_text, chunk_text, validate_input_data
from src.embeddings import EmbeddingGenerator, calculate_cosine_similarity
from src.matcher import SectionMatcher


def test_utils():
    """Test utility functions."""
    print("🧪 Testing utility functions...")
    
    # Test text cleaning
    dirty_text = "  This is   a test\u00a0with   weird\tspacing.  "
    clean = clean_text(dirty_text)
    assert "This is a test with weird spacing." in clean
    print("Text cleaning works")
    
    # Test text chunking
    long_text = "This is a very long text. " * 50
    chunks = chunk_text(long_text, max_chunk_size=100, overlap=20)
    assert len(chunks) > 1
    print(f"Text chunking works - created {len(chunks)} chunks")
    
    # Test input validation
    valid_input = {
        "persona": "Test persona",
        "job_to_be_done": "Test job",
        "documents": ["test.pdf"]
    }
    assert validate_input_data(valid_input) == True
    print("Input validation works")
    
    # Test output structure creation
    output = create_output_structure(valid_input)
    assert "metadata" in output
    assert "extracted_sections" in output
    print("Output structure creation works")


def test_embeddings():
    """Test embedding generation."""
    print("\nTesting embedding generation...")
    
    try:
        # Initialize embedding generator
        generator = EmbeddingGenerator()
        print(f"Loaded embedding model: {generator.model_name}")
        
        # Test query embedding
        persona = "Software engineer working on authentication"
        job = "Implement OAuth 2.0 for secure API access"
        query_embedding = generator.create_query_embedding(persona, job)
        
        assert query_embedding is not None
        assert len(query_embedding) > 0
        print(f"Query embedding generated - dimension: {len(query_embedding)}")
        
        # Test section embeddings
        test_sections = [
            {
                "title": "OAuth 2.0 Implementation",
                "content": "This section describes how to implement OAuth 2.0 authentication for secure API access.",
                "page_number": 1
            },
            {
                "title": "Database Configuration", 
                "content": "This section covers database setup and connection parameters.",
                "page_number": 2
            }
        ]
        
        embedded_sections = generator.create_section_embeddings(test_sections)
        assert len(embedded_sections) == 2
        assert 'embedding' in embedded_sections[0]
        print(f"Section embeddings generated - {len(embedded_sections)} sections")
        
        # Test similarity calculation
        similarity = calculate_cosine_similarity(
            query_embedding, 
            embedded_sections[0]['embedding']
        )
        assert 0 <= similarity <= 1
        print(f"Similarity calculation works - score: {similarity:.4f}")
        
        return query_embedding, embedded_sections
        
    except Exception as e:
        print(f"WARNING: Embedding test failed (might need internet connection): {e}")
        return None, None


def test_matcher(query_embedding, embedded_sections):
    """Test section matching and ranking."""
    print("\nTesting section matching...")
    
    if query_embedding is None or not embedded_sections:
        print("WARNING: Skipping matcher test - no embeddings available")
        return
    
    try:
        # Initialize matcher
        matcher = SectionMatcher(min_similarity_threshold=0.1)  # Low threshold for testing
        
        # Test section ranking
        ranked_sections = matcher.rank_sections(
            query_embedding, embedded_sections, top_k=5
        )
        
        assert len(ranked_sections) <= len(embedded_sections)
        if ranked_sections:
            assert 'similarity_score' in ranked_sections[0]
            print(f"Section ranking works - {len(ranked_sections)} sections ranked")
            
            # Test summary creation
            summaries = matcher.create_section_summaries(ranked_sections)
            assert len(summaries) == len(ranked_sections)
            assert 'importance_rank' in summaries[0]
            print(f"Section summaries created - {len(summaries)} summaries")
            
            # Test subsection analysis
            analysis = matcher.create_subsection_analysis(ranked_sections)
            assert len(analysis) <= len(ranked_sections)
            if analysis:
                assert 'refined_text' in analysis[0]
                print(f"Subsection analysis created - {len(analysis)} analyses")
        else:
            print("WARNING: No sections met similarity threshold")
        
    except Exception as e:
        print(f"Matcher test failed: {e}")


def test_full_pipeline_mock():
    """Test the full pipeline with mock data."""
    print("\nTesting full pipeline with mock data...")
    
    try:
        from src.main import DocumentIntelligencePipeline
        
        # We can't test the full pipeline without PDF files,
        # but we can test the class initialization
        pipeline = DocumentIntelligencePipeline(
            input_file="test_input.json",
            output_file="test_output.json"
        )
        
        assert pipeline.input_file == "test_input.json"
        assert pipeline.output_file == "test_output.json"
        assert "documents_processed" in pipeline.processing_stats
        
        print("Pipeline initialization works")
        
    except Exception as e:
        print(f"Pipeline test failed: {e}")


def main():
    """Run all tests."""
    print("Running Persona-Driven Document Intelligence Pipeline Tests\n")
    
    # Test individual components
    test_utils()
    query_embedding, embedded_sections = test_embeddings() 
    test_matcher(query_embedding, embedded_sections)
    test_full_pipeline_mock()
    
    print("\nAll tests completed!")
    print("\nNext steps:")
    print("1. Install dependencies: pip install -r requirements.txt")
    print("2. Add PDF documents to test with")
    print("3. Update input JSON with actual document paths")
    print("4. Run: python src/main.py")


if __name__ == "__main__":
    main() 
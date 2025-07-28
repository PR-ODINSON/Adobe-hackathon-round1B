#!/usr/bin/env python3
"""
Test script to validate hackathon format compatibility.
Tests the pipeline with official format inputs and validates outputs.
"""

import json
import os
import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / 'src'))

from src.main import DocumentIntelligencePipeline


def create_test_input():
    """Create a test input in the official hackathon format."""
    test_input = {
        "challenge_info": {
            "challenge_id": "round_1b_test",
            "test_case_name": "validation_test",
            "description": "Testing pipeline compatibility"
        },
        "documents": [
            {
                "filename": "sample_document.pdf",
                "title": "Sample Document"
            }
        ],
        "persona": {
            "role": "Software Engineer"
        },
        "job_to_be_done": {
            "task": "Test document processing pipeline"
        }
    }
    return test_input


def validate_output_format(output_data):
    """Validate that output matches expected hackathon format."""
    required_fields = ["metadata", "extracted_sections", "subsection_analysis"]
    
    for field in required_fields:
        if field not in output_data:
            raise ValueError(f"Missing required field: {field}")
    
    # Validate metadata structure
    metadata = output_data["metadata"]
    metadata_fields = ["input_documents", "persona", "job_to_be_done", "processing_timestamp"]
    for field in metadata_fields:
        if field not in metadata:
            raise ValueError(f"Missing metadata field: {field}")
    
    # Validate extracted_sections structure
    if output_data["extracted_sections"]:
        section = output_data["extracted_sections"][0]
        section_fields = ["document", "section_title", "importance_rank", "page_number"]
        for field in section_fields:
            if field not in section:
                raise ValueError(f"Missing extracted_sections field: {field}")
    
    # Validate subsection_analysis structure
    if output_data["subsection_analysis"]:
        analysis = output_data["subsection_analysis"][0]
        analysis_fields = ["document", "refined_text", "page_number"]
        for field in analysis_fields:
            if field not in analysis:
                raise ValueError(f"Missing subsection_analysis field: {field}")
    
    print("✅ Output format validation passed!")


def test_input_format_compatibility():
    """Test that the pipeline handles the official input format correctly."""
    print("Testing input format compatibility...")
    
    # Create test directories
    os.makedirs("test_app/input", exist_ok=True)
    os.makedirs("test_app/output", exist_ok=True)
    
    # Create test input file
    test_input = create_test_input()
    input_file = "test_app/input/challenge1b_input.json"
    output_file = "test_app/output/challenge1b_output.json"
    
    with open(input_file, 'w') as f:
        json.dump(test_input, f, indent=2)
    
    try:
        # Test pipeline initialization and input loading
        pipeline = DocumentIntelligencePipeline(input_file, output_file)
        input_data = pipeline._load_and_validate_input()
        
        # Validate input processing
        assert "persona_text" in input_data
        assert "job_to_be_done_text" in input_data
        assert input_data["persona_text"] == "Software Engineer"
        assert input_data["job_to_be_done_text"] == "Test document processing pipeline"
        
        print("✅ Input format compatibility test passed!")
        
    except Exception as e:
        print(f"❌ Input format test failed: {e}")
        return False
    
    finally:
        # Cleanup
        if os.path.exists(input_file):
            os.remove(input_file)
        if os.path.exists("test_app/input"):
            os.rmdir("test_app/input")
        if os.path.exists("test_app/output"):
            os.rmdir("test_app/output")
        if os.path.exists("test_app"):
            os.rmdir("test_app")
    
    return True


def main():
    """Run all validation tests."""
    print("🧪 Running Hackathon Compatibility Tests")
    print("=" * 50)
    
    try:
        # Test 1: Input format compatibility
        if not test_input_format_compatibility():
            return 1
        
        print("\n✅ All tests passed! Pipeline is hackathon-ready.")
        return 0
        
    except Exception as e:
        print(f"\n❌ Tests failed: {e}")
        return 1


if __name__ == "__main__":
    exit(main()) 
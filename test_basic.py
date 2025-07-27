"""
Basic tests to verify project structure and dependencies.
This test file doesn't require external dependencies like PyMuPDF or sentence-transformers.
"""

import os
import sys
import json


def test_project_structure():
    """Test that all required directories and files exist."""
    print("Testing project structure...")
    
    required_dirs = [
        "app",
        "app/input", 
        "app/output",
        "src"
    ]
    
    required_files = [
        "requirements.txt",
        "README.md",
        "app/input/challenge1b_input.json",
        "src/__init__.py",
        "src/main.py",
        "src/parser.py", 
        "src/embeddings.py",
        "src/matcher.py",
        "src/utils.py"
    ]
    
    all_passed = True
    
    # Check directories
    for dir_path in required_dirs:
        if os.path.exists(dir_path) and os.path.isdir(dir_path):
            print(f"Directory exists: {dir_path}")
        else:
            print(f"ERROR: Missing directory: {dir_path}")
            all_passed = False
    
    # Check files
    for file_path in required_files:
        if os.path.exists(file_path) and os.path.isfile(file_path):
            print(f"File exists: {file_path}")
        else:
            print(f"ERROR: Missing file: {file_path}")
            all_passed = False
    
    return all_passed


def test_input_file():
    """Test the sample input file."""
    print("\nTesting input file...")
    
    input_file = "app/input/challenge1b_input.json"
    
    try:
        with open(input_file, 'r') as f:
            data = json.load(f)
        
        required_fields = ["persona", "job_to_be_done"]
        
        for field in required_fields:
            if field in data:
                print(f"Field exists: {field}")
            else:
                print(f"ERROR: Missing field: {field}")
        
        print("Input file is valid JSON")
        return True
        
    except FileNotFoundError:
        print(f"ERROR: Input file not found: {input_file}")
        return False
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON in input file: {e}")
        return False


def test_utils_functions():
    """Test utility functions that don't require external dependencies."""
    print("\nTesting utility functions...")
    
    try:
        # Add src to path
        sys.path.append('src')
        
        from utils import clean_text, chunk_text, format_section_title, get_timestamp
        
        # Test clean_text
        dirty_text = "  This is   a test\u00a0with   weird\tspacing.  "
        clean = clean_text(dirty_text)
        assert "This is a test with weird spacing." in clean
        print("clean_text function works")
        
        # Test chunk_text
        long_text = "This is a very long text. " * 50
        chunks = chunk_text(long_text, max_chunk_size=100, overlap=20)
        assert len(chunks) > 1
        print(f"chunk_text function works - created {len(chunks)} chunks")
        
        # Test format_section_title
        title = format_section_title("test title")
        assert "Test Title" in title
        print("format_section_title function works")
        
        # Test get_timestamp
        timestamp = get_timestamp()
        assert len(timestamp) > 10  # Basic sanity check
        print("get_timestamp function works")
        
        return True
        
    except ImportError as e:
        print(f"ERROR: Failed to import utils: {e}")
        return False
    except Exception as e:
        print(f"ERROR: Utility function test failed: {e}")
        return False


def test_readme_file():
    """Test that README file exists and has basic content."""
    print("\nTesting README file...")
    
    try:
        with open("README.md", 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for key sections
        required_sections = [
            "# Persona-Driven Document Intelligence",
            "## Installation",
            "## Usage", 
            "## Architecture",
            "## Output Format"
        ]
        
        for section in required_sections:
            if section in content:
                print(f"README contains: {section}")
            else:
                print(f"WARNING: README missing section: {section}")
        
        print(f"README file exists and has content ({len(content)} characters)")
        return True
        
    except FileNotFoundError:
        print("ERROR: README.md file not found")
        return False
    except Exception as e:
        print(f"ERROR: Error reading README: {e}")
        return False


def test_requirements_file():
    """Test that requirements.txt exists and has necessary packages."""
    print("\nTesting requirements file...")
    
    try:
        with open("requirements.txt", 'r') as f:
            content = f.read()
        
        required_packages = [
            "PyMuPDF",
            "sentence-transformers", 
            "numpy",
            "scipy"
        ]
        
        for package in required_packages:
            if package in content:
                print(f"Requirements includes: {package}")
            else:
                print(f"ERROR: Requirements missing: {package}")
        
        return True
        
    except FileNotFoundError:
        print("ERROR: requirements.txt file not found")
        return False
    except Exception as e:
        print(f"ERROR: Error reading requirements: {e}")
        return False


def main():
    """Run all basic tests."""
    print("=== Basic Project Structure Tests ===\n")
    
    tests = [
        test_project_structure,
        test_input_file,
        test_utils_functions,
        test_readme_file,
        test_requirements_file
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n=== Test Results: {passed}/{total} tests passed ===")
    
    if passed == total:
        print("Basic tests completed!")
    else:
        print("Some tests failed - check the output above")
    
    print("\nFor Adobe Hackathon evaluation:")
    print("1. Ensure all files are in place")
    print("2. Run: python src/main.py")
    print("3. Check output in /app/output/challenge1b_output.json")


if __name__ == "__main__":
    main() 
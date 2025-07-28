"""
Main entry point for the Persona-Driven Document Intelligence pipeline.
Orchestrates the complete process from input parsing to output generation.
"""

import os
import sys
import glob
from typing import List, Dict, Any

# Add src to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from .parser import parse_document
from .embeddings import create_embeddings
from .matcher import match_and_rank_sections
from .utils import (
    load_json, save_json, validate_input_data, 
    create_output_structure, get_timestamp
)


class DocumentIntelligencePipeline:
    """Main pipeline for persona-driven document intelligence."""
    
    def __init__(self, input_file: str = "/app/input/challenge1b_input.json",
                 output_file: str = "/app/output/challenge1b_output.json"):
        """
        Initialize the pipeline.
        
        Args:
            input_file: Path to input JSON file
            output_file: Path to output JSON file
        """
        self.input_file = input_file
        self.output_file = output_file
        self.processing_stats = {
            "documents_processed": 0,
            "sections_extracted": 0,
            "sections_ranked": 0,
            "processing_time": 0
        }
    
    def run(self) -> Dict[str, Any]:
        """
        Execute the complete document intelligence pipeline.
        
        Returns:
            Dictionary containing the processed results
        """
        print("Starting Persona-Driven Document Intelligence Pipeline...")
        
        try:
            # Step 1: Load and validate input
            print("Loading input data...")
            input_data = self._load_and_validate_input()
            
            # Step 2: Auto-discover and validate PDF files
            print("Discovering PDF files...")
            pdf_files = self._discover_pdf_files()
            
            # Step 3: Extract sections from all documents
            print("Extracting sections from documents...")
            all_sections = self._extract_all_sections(pdf_files)
            
            # Step 4: Create embeddings
            print("Generating embeddings...")
            query_embedding, embedded_sections = self._create_embeddings(
                input_data, all_sections
            )
            
            # Step 5: Match and rank sections
            print("Matching and ranking sections...")
            section_summaries, subsection_analysis = self._match_sections(
                query_embedding, embedded_sections
            )
            
            # Step 6: Create output structure
            print("Generating output...")
            output_data = self._create_output(
                input_data, section_summaries, subsection_analysis, pdf_files
            )
            
            # Step 7: Save results
            self._save_output(output_data)
            
            print("Pipeline completed successfully!")
            print(f"Processed {self.processing_stats['documents_processed']} documents")
            print(f"Extracted {self.processing_stats['sections_extracted']} sections")
            print(f"Ranked {self.processing_stats['sections_ranked']} relevant sections")
            
            return output_data
            
        except Exception as e:
            print(f"Pipeline failed: {e}")
            raise
    
    def _load_and_validate_input(self) -> Dict[str, Any]:
        """Load and validate input JSON data."""
        if not os.path.exists(self.input_file):
            raise FileNotFoundError(f"Required input file not found: {self.input_file}")
        
        try:
            input_data = load_json(self.input_file)
        except Exception as e:
            raise ValueError(f"Failed to parse input JSON file {self.input_file}: {e}")
        
        # Validate required fields for hackathon format
        required_fields = ["persona", "job_to_be_done"]
        for field in required_fields:
            if field not in input_data:
                raise ValueError(f"Missing required field in input JSON: {field}")
        
        # Handle both old format (direct strings) and new format (nested objects)
        if isinstance(input_data["persona"], dict):
            if "role" not in input_data["persona"]:
                raise ValueError("Missing 'role' field in persona object")
            input_data["persona_text"] = input_data["persona"]["role"]
        else:
            input_data["persona_text"] = input_data["persona"]
        
        if isinstance(input_data["job_to_be_done"], dict):
            if "task" not in input_data["job_to_be_done"]:
                raise ValueError("Missing 'task' field in job_to_be_done object")
            input_data["job_to_be_done_text"] = input_data["job_to_be_done"]["task"]
        else:
            input_data["job_to_be_done_text"] = input_data["job_to_be_done"]
        
        return input_data
    
    def _discover_pdf_files(self) -> List[str]:
        """Auto-discover all PDF files in /app/input/ directory."""
        input_dir = "/app/input"
        
        if not os.path.exists(input_dir):
            raise FileNotFoundError(f"Input directory not found: {input_dir}")
        
        # Find all PDF files
        pdf_pattern = os.path.join(input_dir, "*.pdf")
        pdf_files = glob.glob(pdf_pattern, recursive=False)
        
        # Also check for case variations
        pdf_pattern_upper = os.path.join(input_dir, "*.PDF")
        pdf_files.extend(glob.glob(pdf_pattern_upper, recursive=False))
        
        # Remove duplicates and sort
        pdf_files = sorted(list(set(pdf_files)))
        
        if not pdf_files:
            print(f"WARNING: No PDF files found in {input_dir}")
            print("The pipeline will continue but may not produce meaningful results.")
        else:
            print(f"Found {len(pdf_files)} PDF files:")
            for pdf_file in pdf_files:
                print(f"  - {os.path.basename(pdf_file)}")
        
        return pdf_files
    
    def _extract_all_sections(self, pdf_files: List[str]) -> List[Dict[str, Any]]:
        """Extract sections from all PDF documents."""
        all_sections = []
        
        for doc_path in pdf_files:
            if not os.path.exists(doc_path):
                print(f"Warning: Document not found: {doc_path}")
                continue
            
            # Verify it's actually a PDF file
            if not doc_path.lower().endswith('.pdf'):
                print(f"Skipping non-PDF file: {os.path.basename(doc_path)}")
                continue
            
            try:
                print(f"  Processing: {os.path.basename(doc_path)}")
                sections = parse_document(doc_path)
                
                # Add document name to each section
                doc_name = os.path.basename(doc_path)
                for section in sections:
                    section['document'] = doc_name
                
                all_sections.extend(sections)
                self.processing_stats["documents_processed"] += 1
                
            except Exception as e:
                print(f"Error processing {doc_path}: {e}")
                continue
        
        self.processing_stats["sections_extracted"] = len(all_sections)
        
        if not all_sections:
            print("Warning: No sections could be extracted from any documents")
            # Don't raise an error, just continue with empty sections
        
        return all_sections
    
    def _create_embeddings(self, input_data: Dict[str, Any], 
                          sections: List[Dict[str, Any]]) -> tuple:
        """Create embeddings for query and document sections."""
        persona = input_data["persona_text"]
        job_to_be_done = input_data["job_to_be_done_text"]
        
        query_embedding, embedded_sections = create_embeddings(
            persona, job_to_be_done, sections
        )
        
        return query_embedding, embedded_sections
    
    def _match_sections(self, query_embedding, embedded_sections) -> tuple:
        """Match and rank sections based on relevance."""
        section_summaries, subsection_analysis = match_and_rank_sections(
            query_embedding, embedded_sections, top_k=10
        )
        
        self.processing_stats["sections_ranked"] = len(section_summaries)
        
        return section_summaries, subsection_analysis
    
    def _create_output(self, input_data: Dict[str, Any], 
                      section_summaries: List[Dict[str, Any]], 
                      subsection_analysis: List[Dict[str, Any]],
                      pdf_files: List[str]) -> Dict[str, Any]:
        """Create the final output structure in hackathon format."""
        # Extract persona and job_to_be_done for output (use original format)
        persona_text = input_data["persona_text"]
        job_to_be_done_text = input_data["job_to_be_done_text"]
        
        # Create base output structure matching hackathon format
        output_data = {
            "metadata": {
                "input_documents": [os.path.basename(f) for f in pdf_files],
                "persona": persona_text,
                "job_to_be_done": job_to_be_done_text,
                "processing_timestamp": get_timestamp()
            },
            "extracted_sections": section_summaries,
            "subsection_analysis": subsection_analysis
        }
        
        return output_data
    
    def _save_output(self, output_data: Dict[str, Any]) -> None:
        """Save the output data to JSON file."""
        # Ensure output directory exists
        output_dir = os.path.dirname(self.output_file)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        
        save_json(output_data, self.output_file)
        print(f"Results saved to: {self.output_file}")


def main():
    """Main function to run the pipeline."""
    # Use hardcoded paths for Docker evaluation
    input_file = "/app/input/challenge1b_input.json"
    output_file = "/app/output/challenge1b_output.json"
    
    # Create and run pipeline
    pipeline = DocumentIntelligencePipeline(input_file, output_file)
    
    try:
        result = pipeline.run()
        return result
    except KeyboardInterrupt:
        print("\nPipeline interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Pipeline failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    pipeline = DocumentIntelligencePipeline(
        input_file="/app/input/challenge1b_input.json",
        output_file="/app/output/challenge1b_output.json"
    )
    pipeline.run() 
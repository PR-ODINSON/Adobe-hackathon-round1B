"""
PDF Parser module for extracting sections and content from PDF documents.
Uses PyMuPDF (fitz) for PDF processing and text extraction.
"""

import fitz  # PyMuPDF
import re
from typing import List, Dict, Tuple, Any
from .utils import clean_text, format_section_title


class PDFSection:
    """Represents a section extracted from a PDF."""
    
    def __init__(self, title: str, content: str, page_number: int, level: int = 1):
        self.title = format_section_title(title)
        self.content = clean_text(content)
        self.page_number = page_number
        self.level = level  # Heading level (1, 2, 3, etc.)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert section to dictionary format."""
        return {
            "title": self.title,
            "content": self.content,
            "page_number": self.page_number,
            "level": self.level
        }


class PDFParser:
    """Parser for extracting structured content from PDF documents."""
    
    def __init__(self):
        # Patterns to identify section headings
        self.heading_patterns = [
            # Numbered sections (1., 1.1, etc.)
            r'^(\d+\.)+\s*(.+)$',
            # Roman numerals
            r'^[IVX]+\.\s*(.+)$',
            # Letters (A., B., etc.)
            r'^[A-Z]\.\s*(.+)$',
            # All caps headers
            r'^[A-Z\s]{3,}$',
            # Title case headers (at least 2 words, starting with capital)
            r'^[A-Z][a-z]+(\s+[A-Z][a-z]*)+.*$'
        ]
        
        # Minimum and maximum lengths for valid headings
        self.min_heading_length = 3
        self.max_heading_length = 200
    
    def extract_text_from_pdf(self, pdf_path: str) -> List[Dict[str, Any]]:
        """
        Extract text content from PDF with page information.
        
        Returns:
            List of dictionaries with page_number and text content
        """
        try:
            doc = fitz.open(pdf_path)
            pages_content = []
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text = page.get_text()
                
                if text.strip():  # Only include pages with content
                    pages_content.append({
                        "page_number": page_num + 1,
                        "text": clean_text(text)
                    })
            
            doc.close()
            return pages_content
            
        except Exception as e:
            raise ValueError(f"Error processing PDF {pdf_path}: {e}")
    
    def identify_headings(self, text: str) -> List[Tuple[str, int]]:
        """
        Identify potential headings in text.
        
        Returns:
            List of (heading_text, confidence_level) tuples
        """
        lines = text.split('\n')
        headings = []
        
        for line in lines:
            line = line.strip()
            
            # Skip empty lines or very short/long lines
            if not line or len(line) < self.min_heading_length or len(line) > self.max_heading_length:
                continue
            
            confidence = self._calculate_heading_confidence(line)
            
            if confidence > 0:
                headings.append((line, confidence))
        
        return headings
    
    def _calculate_heading_confidence(self, line: str) -> int:
        """
        Calculate confidence that a line is a heading.
        Returns confidence score (0-100).
        """
        confidence = 0
        
        # Check against heading patterns
        for pattern in self.heading_patterns:
            if re.match(pattern, line.strip()):
                confidence += 30
                break
        
        # Additional heuristics
        
        # Shorter lines are more likely to be headings
        if len(line) < 80:
            confidence += 10
        
        # Lines ending with colon often introduce sections
        if line.endswith(':'):
            confidence += 15
        
        # Lines with title case formatting
        words = line.split()
        if len(words) >= 2 and all(word[0].isupper() for word in words if word):
            confidence += 20
        
        # Lines that are all uppercase (but not too long)
        if line.isupper() and len(line) < 50:
            confidence += 25
        
        # Penalize lines with common non-heading indicators
        if any(indicator in line.lower() for indicator in ['.', ',', ';', '?', '!', 'the', 'and', 'of', 'in', 'to']):
            confidence -= 10
        
        # Boost for lines that start with common section words
        section_starters = ['chapter', 'section', 'part', 'appendix', 'introduction', 'conclusion', 'summary', 'overview']
        if any(line.lower().startswith(starter) for starter in section_starters):
            confidence += 20
        
        return max(0, min(100, confidence))
    
    def extract_sections(self, pdf_path: str, min_confidence: int = 30) -> List[PDFSection]:
        """
        Extract sections from PDF document.
        
        Args:
            pdf_path: Path to PDF file
            min_confidence: Minimum confidence threshold for heading detection
        
        Returns:
            List of PDFSection objects
        """
        pages_content = self.extract_text_from_pdf(pdf_path)
        sections = []
        current_section = None
        
        for page_data in pages_content:
            page_num = page_data["page_number"]
            text = page_data["text"]
            
            # Identify headings in this page
            headings = self.identify_headings(text)
            
            if not headings:
                # No headings found, add content to current section
                if current_section:
                    current_section.content += " " + text
                else:
                    # Create a default section for content without headings
                    current_section = PDFSection(
                        title=f"Content from Page {page_num}",
                        content=text,
                        page_number=page_num
                    )
                continue
            
            # Process text with headings
            lines = text.split('\n')
            heading_lines = {heading[0]: heading[1] for heading in headings if heading[1] >= min_confidence}
            
            content_buffer = []
            
            for line in lines:
                line_stripped = line.strip()
                
                if line_stripped in heading_lines:
                    # Save previous section if exists
                    if current_section and content_buffer:
                        current_section.content += " " + " ".join(content_buffer)
                        sections.append(current_section)
                    
                    # Start new section
                    current_section = PDFSection(
                        title=line_stripped,
                        content="",
                        page_number=page_num,
                        level=self._estimate_heading_level(line_stripped)
                    )
                    content_buffer = []
                else:
                    # Add to content
                    if line_stripped:
                        content_buffer.append(line_stripped)
            
            # Add remaining content to current section
            if current_section and content_buffer:
                current_section.content += " " + " ".join(content_buffer)
        
        # Add final section
        if current_section:
            sections.append(current_section)
        
        return self._post_process_sections(sections)
    
    def _estimate_heading_level(self, heading: str) -> int:
        """Estimate the hierarchical level of a heading."""
        # Check for numbered patterns
        numbered_match = re.match(r'^(\d+\.)+', heading)
        if numbered_match:
            return heading.count('.')
        
        # Other heuristics
        if heading.isupper():
            return 1  # All caps usually top level
        
        if re.match(r'^[A-Z]\.\s', heading):
            return 2  # Letter enumeration
        
        return 2  # Default level
    
    def _post_process_sections(self, sections: List[PDFSection]) -> List[PDFSection]:
        """Post-process sections to clean up and merge where appropriate."""
        if not sections:
            return sections
        
        processed_sections = []
        
        for section in sections:
            # Skip sections with minimal content
            if len(section.content.strip()) < 50:
                continue
            
            # Clean up content
            section.content = clean_text(section.content)
            
            processed_sections.append(section)
        
        return processed_sections


def parse_document(pdf_path: str) -> List[Dict[str, Any]]:
    """
    Main function to parse a PDF document and extract sections.
    
    Args:
        pdf_path: Path to the PDF file
    
    Returns:
        List of section dictionaries
    """
    parser = PDFParser()
    sections = parser.extract_sections(pdf_path)
    
    return [section.to_dict() for section in sections] 
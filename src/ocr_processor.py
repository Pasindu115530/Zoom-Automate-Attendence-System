"""
OCR Processor Module for Zoom Attendance System
Handles optical character recognition to extract student names and registration numbers
"""

import pytesseract
import cv2
import numpy as np
import re
from datetime import datetime


class OCRProcessor:
    """Handles OCR text extraction and parsing"""
    
    def __init__(self, tesseract_path=None):
        """
        Initialize OCR processor
        
        Args:
            tesseract_path: Path to tesseract executable (Windows only)
        """
        if tesseract_path:
            pytesseract.pytesseract.pytesseract_cmd = tesseract_path
        
        self.last_extracted_text = None
        self.last_extraction_time = None
    
    def extract_text(self, image):
        """
        Extract text from image using Tesseract OCR
        
        Args:
            image: Image to process (numpy array)
            
        Returns:
            Extracted text string
        """
        try:
            if image is None:
                return None
            
            # Convert to appropriate format for OCR
            if len(image.shape) == 3:
                # If color image, convert to grayscale
                image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Extract text
            text = pytesseract.image_to_string(image)
            
            self.last_extracted_text = text
            self.last_extraction_time = datetime.now()
            
            return text
            
        except Exception as e:
            print(f"✗ OCR extraction error: {e}")
            return None
    
    def extract_text_with_details(self, image):
        """
        Extract text with additional details (confidence, bounding boxes)
        
        Args:
            image: Image to process
            
        Returns:
            Dictionary with text and metadata
        """
        try:
            if image is None:
                return None
            
            if len(image.shape) == 3:
                image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Get detailed information
            data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
            
            result = {
                "text": pytesseract.image_to_string(image),
                "confidence": data.get("conf", []),
                "boxes": data,
                "timestamp": datetime.now()
            }
            
            return result
            
        except Exception as e:
            print(f"✗ OCR details extraction error: {e}")
            return None
    
    def parse_student_info(self, text):
        """
        Parse extracted text to find student names and registration numbers
        
        Args:
            text: Raw text from OCR
            
        Returns:
            List of dictionaries with student info
        """
        try:
            if not text:
                return []
            
            students = []
            lines = text.strip().split('\n')
            
            for line in lines:
                line = line.strip()
                
                if not line or len(line) < 3:
                    continue
                
                # Try to extract registration number (e.g., REG001, REG123)
                reg_match = re.search(r'REG\s*(\d+)', line, re.IGNORECASE)
                
                if reg_match:
                    reg_number = "REG" + reg_match.group(1)
                    
                    # Extract name (everything before registration number)
                    name_part = line[:reg_match.start()].strip()
                    
                    if name_part:
                        students.append({
                            "name": name_part,
                            "registration_number": reg_number,
                            "raw_line": line,
                            "confidence": 0.0
                        })
            
            return students
            
        except Exception as e:
            print(f"✗ Student info parsing error: {e}")
            return []
    
    def clean_text(self, text):
        """
        Clean OCR extracted text
        Remove artifacts, fix common OCR mistakes
        
        Args:
            text: Raw OCR text
            
        Returns:
            Cleaned text
        """
        try:
            if not text:
                return ""
            
            # Remove common OCR artifacts
            text = re.sub(r'[^\w\s\-\.]', '', text)  # Remove special characters
            text = re.sub(r'\s+', ' ', text)  # Normalize whitespace
            text = re.sub(r'(\d)\s+(\d)', r'\1\2', text)  # Remove spaces in numbers
            
            # Fix common substitutions
            replacements = {
                '0': 'O',  # Zero to O in names (context-dependent)
                'I': 'l',  # Capital I to lowercase l
            }
            
            return text.strip()
            
        except Exception as e:
            print(f"✗ Text cleaning error: {e}")
            return text
    
    def extract_names_and_ids(self, text):
        """
        Extract names and IDs in various formats
        
        Args:
            text: OCR extracted text
            
        Returns:
            List of tuples (name, registration_number)
        """
        try:
            results = []
            lines = text.strip().split('\n')
            
            for line in lines:
                line = line.strip()
                
                # Pattern 1: Name followed by REG number
                # e.g., "Ahmed Ali REG001" or "Ahmed Ali, REG001"
                match = re.search(r'(.+?)\s*(?:,|\s+)(REG\s*\d+)', line, re.IGNORECASE)
                if match:
                    name = match.group(1).strip()
                    reg = match.group(2).replace(' ', '').upper()
                    results.append((name, reg))
                    continue
                
                # Pattern 2: REG number followed by name
                # e.g., "REG001 Ahmed Ali"
                match = re.search(r'(REG\s*\d+)\s+(.+)', line, re.IGNORECASE)
                if match:
                    reg = match.group(1).replace(' ', '').upper()
                    name = match.group(2).strip()
                    results.append((name, reg))
                    continue
            
            return results
            
        except Exception as e:
            print(f"✗ Name/ID extraction error: {e}")
            return []
    
    def get_confidence_score(self, image, text):
        """
        Calculate confidence score for OCR result
        
        Args:
            image: Original image
            text: Extracted text
            
        Returns:
            Confidence score (0.0 to 1.0)
        """
        try:
            if not text or image is None:
                return 0.0
            
            # Get detailed OCR data with confidence
            if len(image.shape) == 3:
                image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
            confidences = [int(c) for c in data.get('conf', []) if int(c) > -1]
            
            if not confidences:
                return 0.0
            
            avg_confidence = sum(confidences) / len(confidences) / 100.0
            return min(max(avg_confidence, 0.0), 1.0)
            
        except Exception as e:
            print(f"✗ Confidence calculation error: {e}")
            return 0.0
    
    def compare_extractions(self, text1, text2):
        """
        Compare two OCR extractions to check if they're the same
        
        Args:
            text1: First extraction
            text2: Second extraction
            
        Returns:
            Similarity score (0.0 to 1.0)
        """
        try:
            if not text1 or not text2:
                return 0.0
            
            # Simple similarity: percentage of common lines
            lines1 = set(text1.lower().split('\n'))
            lines2 = set(text2.lower().split('\n'))
            
            if not lines1 or not lines2:
                return 0.0
            
            common = len(lines1.intersection(lines2))
            total = len(lines1.union(lines2))
            
            return common / total if total > 0 else 0.0
            
        except Exception as e:
            print(f"✗ Comparison error: {e}")
            return 0.0


class OCRCache:
    """Cache OCR results to avoid processing same image repeatedly"""
    
    def __init__(self, max_size=100):
        """
        Initialize OCR cache
        
        Args:
            max_size: Maximum cache size
        """
        self.cache = {}
        self.max_size = max_size
    
    def get_hash(self, image):
        """
        Get hash of image for caching
        
        Args:
            image: Image to hash
            
        Returns:
            Hash string
        """
        try:
            if image is None:
                return None
            
            # Create simple hash from image
            h = hash(image.tobytes())
            return str(h)
            
        except Exception as e:
            print(f"✗ Hash error: {e}")
            return None
    
    def get(self, image):
        """
        Get cached OCR result
        
        Args:
            image: Image to look up
            
        Returns:
            Cached result or None
        """
        h = self.get_hash(image)
        if h and h in self.cache:
            return self.cache[h]
        return None
    
    def set(self, image, result):
        """
        Cache OCR result
        
        Args:
            image: Image that was processed
            result: OCR result
        """
        h = self.get_hash(image)
        if h:
            if len(self.cache) >= self.max_size:
                # Remove oldest entry
                self.cache.pop(next(iter(self.cache)))
            
            self.cache[h] = result
    
    def clear(self):
        """Clear all cache"""
        self.cache.clear()


def main():
    """Test OCR processor"""
    try:
        print("Testing OCR Processor...\n")
        
        ocr = OCRProcessor()
        
        # Sample text that OCR might extract
        sample_text = """
        Ahmed Ali REG001
        Fatima Khan REG002
        Hassan Mohamed REG003
        Layla Ahmed REG004
        """
        
        print("Sample text:")
        print(sample_text)
        print("\nParsing students...")
        
        students = ocr.parse_student_info(sample_text)
        
        for student in students:
            print(f"  ✓ {student['name']} ({student['registration_number']})")
        
        print("\n✓ OCR processor test complete!")
        
    except Exception as e:
        print(f"✗ Test error: {e}")


if __name__ == "__main__":
    main()
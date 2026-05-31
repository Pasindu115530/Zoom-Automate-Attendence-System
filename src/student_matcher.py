"""
Student Matcher Module for Zoom Attendance System
Matches OCR extracted names with student database
"""

import csv
import json
from difflib import SequenceMatcher
from fuzzywuzzy import fuzz
from datetime import datetime


class StudentMatcher:
    """Matches extracted student names with database"""
    
    def __init__(self, database_path="data/students.csv"):
        """
        Initialize student matcher
        
        Args:
            database_path: Path to student database CSV
        """
        self.database_path = database_path
        self.students = []
        self.load_database()
    
    def load_database(self):
        """Load student database from CSV"""
        try:
            with open(self.database_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                self.students = list(reader)
            
            print(f"✓ Loaded {len(self.students)} students from {self.database_path}")
            return True
            
        except FileNotFoundError:
            print(f"✗ Student database not found: {self.database_path}")
            return False
        except Exception as e:
            print(f"✗ Error loading database: {e}")
            return False
    
    def reload_database(self):
        """Reload student database"""
        self.students = []
        return self.load_database()
    
    def get_all_students(self):
        """
        Get all students from database
        
        Returns:
            List of student dictionaries
        """
        return self.students
    
    def find_student_by_name(self, name, threshold=0.85):
        """
        Find student by name (fuzzy matching)
        
        Args:
            name: Name to search for
            threshold: Match threshold (0.0 to 1.0)
            
        Returns:
            Matching student dict or None
        """
        if not name or not self.students:
            return None
        
        best_match = None
        best_score = 0
        
        for student in self.students:
            db_name = student.get('Name', '').lower()
            search_name = name.lower().strip()
            
            # Use fuzzywuzzy for better matching
            score = fuzz.token_set_ratio(search_name, db_name) / 100.0
            
            if score > best_score:
                best_score = score
                best_match = student
        
        if best_score >= threshold:
            return {
                "student": best_match,
                "confidence": best_score
            }
        
        return None
    
    def find_student_by_registration(self, reg_number):
        """
        Find student by registration number (exact match)
        
        Args:
            reg_number: Registration number to search for
            
        Returns:
            Matching student dict or None
        """
        if not reg_number or not self.students:
            return None
        
        search_reg = reg_number.upper().strip()
        
        for student in self.students:
            db_reg = student.get('Registration_Number', '').upper().strip()
            
            if db_reg == search_reg:
                return {
                    "student": student,
                    "confidence": 1.0,
                    "method": "exact_registration"
                }
        
        return None
    
    def match_student(self, name, registration_number=None, name_threshold=0.85):
        """
        Match student using name and/or registration number
        
        Args:
            name: Student name
            registration_number: Registration number (optional)
            name_threshold: Matching threshold for name
            
        Returns:
            Matching student info or None
        """
        if not name and not registration_number:
            return None
        
        # Try exact registration match first (most reliable)
        if registration_number:
            result = self.find_student_by_registration(registration_number)
            if result:
                return result
        
        # Fall back to name matching
        if name:
            result = self.find_student_by_name(name, threshold=name_threshold)
            if result:
                result["method"] = "fuzzy_name"
                return result
        
        return None
    
    def match_multiple_students(self, extracted_students, name_threshold=0.85):
        """
        Match multiple students at once
        
        Args:
            extracted_students: List of (name, registration) tuples from OCR
            name_threshold: Matching threshold
            
        Returns:
            List of matched student dicts
        """
        matched = []
        
        for name, reg_number in extracted_students:
            result = self.match_student(name, reg_number, name_threshold)
            
            if result:
                result["extracted_name"] = name
                result["extracted_reg"] = reg_number
                matched.append(result)
        
        return matched
    
    def get_similarity_score(self, text1, text2):
        """
        Calculate text similarity score
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score (0.0 to 1.0)
        """
        if not text1 or not text2:
            return 0.0
        
        # Use fuzzywuzzy for better matching
        score = fuzz.token_set_ratio(text1.lower(), text2.lower()) / 100.0
        return score
    
    def generate_match_report(self, matched_students):
        """
        Generate report of matched students
        
        Args:
            matched_students: List of matched student dicts
            
        Returns:
            Formatted report string
        """
        report = []
        report.append("=" * 70)
        report.append("STUDENT MATCHING REPORT")
        report.append("=" * 70)
        report.append(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Total matches: {len(matched_students)}\n")
        
        for i, match in enumerate(matched_students, 1):
            student = match.get("student", {})
            confidence = match.get("confidence", 0)
            method = match.get("method", "unknown")
            
            report.append(f"{i}. {student.get('Name', 'Unknown')}")
            report.append(f"   Registration: {student.get('Registration_Number', 'N/A')}")
            report.append(f"   Extracted as: {match.get('extracted_name', 'N/A')}")
            report.append(f"   Confidence: {confidence:.2%}")
            report.append(f"   Method: {method}")
            report.append("")
        
        return "\n".join(report)
    
    def filter_by_confidence(self, matched_students, min_confidence=0.7):
        """
        Filter matched students by confidence score
        
        Args:
            matched_students: List of matched students
            min_confidence: Minimum confidence threshold
            
        Returns:
            Filtered list
        """
        return [
            s for s in matched_students 
            if s.get("confidence", 0) >= min_confidence
        ]
    
    def get_unmatched_from_database(self, matched_students):
        """
        Get students from database who were not matched
        
        Args:
            matched_students: List of matched students
            
        Returns:
            List of unmatched students
        """
        matched_names = {
            m["student"].get("Name", "").lower() 
            for m in matched_students
        }
        
        unmatched = [
            s for s in self.students 
            if s.get("Name", "").lower() not in matched_names
        ]
        
        return unmatched
    
    def export_matches_to_csv(self, matched_students, output_file):
        """
        Export matched students to CSV
        
        Args:
            matched_students: List of matched students
            output_file: Output CSV file path
        """
        try:
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                fieldnames = [
                    'Timestamp',
                    'Name',
                    'Registration_Number',
                    'Extracted_Name',
                    'Confidence',
                    'Method'
                ]
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                
                for match in matched_students:
                    student = match.get("student", {})
                    writer.writerow({
                        'Timestamp': datetime.now().isoformat(),
                        'Name': student.get('Name', ''),
                        'Registration_Number': student.get('Registration_Number', ''),
                        'Extracted_Name': match.get('extracted_name', ''),
                        'Confidence': f"{match.get('confidence', 0):.2%}",
                        'Method': match.get('method', '')
                    })
            
            print(f"✓ Exported matches to {output_file}")
            
        except Exception as e:
            print(f"✗ Error exporting matches: {e}")
    
    def get_statistics(self, matched_students):
        """
        Get matching statistics
        
        Args:
            matched_students: List of matched students
            
        Returns:
            Dictionary with statistics
        """
        if not matched_students:
            return {
                "total_matches": 0,
                "average_confidence": 0,
                "high_confidence": 0
            }
        
        confidences = [m.get("confidence", 0) for m in matched_students]
        high_confidence_count = sum(1 for c in confidences if c >= 0.9)
        
        return {
            "total_matches": len(matched_students),
            "average_confidence": sum(confidences) / len(confidences),
            "high_confidence": high_confidence_count,
            "min_confidence": min(confidences),
            "max_confidence": max(confidences)
        }


def main():
    """Test student matcher"""
    try:
        print("Testing Student Matcher...\n")
        
        matcher = StudentMatcher("data/students.csv")
        
        # Test single student match
        print("Testing name matching...")
        result = matcher.match_student("Ahmed Ali")
        if result:
            print(f"  ✓ Found: {result['student'].get('Name')} ({result['confidence']:.2%})")
        
        # Test registration match
        print("\nTesting registration matching...")
        result = matcher.find_student_by_registration("REG001")
        if result:
            print(f"  ✓ Found: {result['student'].get('Name')}")
        
        # Test multiple matches
        print("\nTesting multiple student matching...")
        extracted = [
            ("Ahmed Ali", "REG001"),
            ("Fatima Khan", "REG002"),
            ("Hassan Mohamed", "REG003")
        ]
        
        matched = matcher.match_multiple_students(extracted)
        print(f"  ✓ Matched {len(matched)} students")
        
        print("\n✓ Student matcher test complete!")
        
    except Exception as e:
        print(f"✗ Test error: {e}")


if __name__ == "__main__":
    main()
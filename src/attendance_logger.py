"""
Attendance Logger Module for Zoom Attendance System
Records and manages attendance data
"""

import csv
import json
import os
from datetime import datetime
from pathlib import Path


class AttendanceLogger:
    """Handles attendance logging and reporting"""
    
    def __init__(self, log_dir="logs"):
        """
        Initialize attendance logger
        
        Args:
            log_dir: Directory for log files
        """
        self.log_dir = log_dir
        self.current_date = datetime.now().strftime("%Y-%m-%d")
        self.log_file = f"{log_dir}/attendance_{self.current_date}.csv"
        self.records = []
        
        # Create log directory if needed
        self.create_log_directory()
        
        # Create log file if needed
        self.create_log_file()
    
    def create_log_directory(self):
        """Create log directory if it doesn't exist"""
        try:
            Path(self.log_dir).mkdir(parents=True, exist_ok=True)
            print(f"✓ Log directory: {self.log_dir}")
        except Exception as e:
            print(f"✗ Error creating log directory: {e}")
    
    def create_log_file(self):
        """Create log file with headers if it doesn't exist"""
        try:
            if not os.path.exists(self.log_file):
                with open(self.log_file, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow([
                        "Timestamp",
                        "Student_Name",
                        "Registration_Number",
                        "Email",
                        "Status",
                        "Method",
                        "Confidence",
                        "Notes"
                    ])
                print(f"✓ Created log file: {self.log_file}")
            else:
                print(f"✓ Using existing log file: {self.log_file}")
        except Exception as e:
            print(f"✗ Error creating log file: {e}")
    
    def log_attendance(self, student_info, status="admitted", method="auto", confidence=0.0, notes=""):
        """
        Log student attendance
        
        Args:
            student_info: Dictionary with student info
            status: Status (admitted, present, absent, etc.)
            method: How student was admitted (auto, manual, ocr, etc.)
            confidence: Confidence score (0.0 to 1.0)
            notes: Additional notes
            
        Returns:
            True if successful
        """
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
            
            record = {
                "Timestamp": timestamp,
                "Student_Name": student_info.get("Name", "Unknown"),
                "Registration_Number": student_info.get("Registration_Number", "N/A"),
                "Email": student_info.get("Email", "N/A"),
                "Status": status,
                "Method": method,
                "Confidence": f"{confidence:.2%}" if confidence else "",
                "Notes": notes
            }
            
            # Append to file
            with open(self.log_file, 'a', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=record.keys())
                writer.writerow(record)
            
            # Keep in memory
            self.records.append(record)
            
            return True
            
        except Exception as e:
            print(f"✗ Error logging attendance: {e}")
            return False
    
    def log_batch_attendance(self, students_list, status="admitted", method="auto"):
        """
        Log multiple students at once
        
        Args:
            students_list: List of student dictionaries
            status: Status for all students
            method: Method for all students
            
        Returns:
            Number of successfully logged students
        """
        success_count = 0
        
        for student in students_list:
            confidence = student.get("confidence", 0.0)
            if self.log_attendance(student, status, method, confidence):
                success_count += 1
        
        return success_count
    
    def get_today_attendance(self):
        """
        Get today's attendance records
        
        Returns:
            List of attendance records
        """
        return self.records
    
    def get_student_attendance(self, student_name):
        """
        Get attendance records for specific student
        
        Args:
            student_name: Student name to search
            
        Returns:
            List of matching records
        """
        return [
            r for r in self.records 
            if r["Student_Name"].lower() == student_name.lower()
        ]
    
    def get_attendance_by_status(self, status):
        """
        Get all records with specific status
        
        Args:
            status: Status to filter by
            
        Returns:
            List of records with that status
        """
        return [
            r for r in self.records 
            if r["Status"].lower() == status.lower()
        ]
    
    def export_to_json(self, output_file=None):
        """
        Export attendance to JSON file
        
        Args:
            output_file: Output file path
            
        Returns:
            True if successful
        """
        try:
            if not output_file:
                date_str = datetime.now().strftime("%Y-%m-%d_%H%M%S")
                output_file = f"{self.log_dir}/attendance_{date_str}.json"
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(self.records, f, indent=2, default=str)
            
            print(f"✓ Exported to {output_file}")
            return True
            
        except Exception as e:
            print(f"✗ Export error: {e}")
            return False
    
    def generate_summary_report(self):
        """
        Generate attendance summary report
        
        Returns:
            Formatted report string
        """
        report = []
        report.append("=" * 70)
        report.append("ATTENDANCE SUMMARY REPORT")
        report.append("=" * 70)
        report.append(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # Statistics by status
        statuses = {}
        for record in self.records:
            status = record.get("Status", "unknown")
            statuses[status] = statuses.get(status, 0) + 1
        
        report.append("Statistics by Status:")
        total = len(self.records)
        for status, count in sorted(statuses.items()):
            percentage = (count / total * 100) if total > 0 else 0
            report.append(f"  {status}: {count} ({percentage:.1f}%)")
        
        report.append(f"\nTotal Records: {total}\n")
        
        # Statistics by method
        methods = {}
        for record in self.records:
            method = record.get("Method", "unknown")
            methods[method] = methods.get(method, 0) + 1
        
        report.append("Statistics by Method:")
        for method, count in sorted(methods.items()):
            percentage = (count / total * 100) if total > 0 else 0
            report.append(f"  {method}: {count} ({percentage:.1f}%)")
        
        # Average confidence
        confidences = []
        for record in self.records:
            conf_str = record.get("Confidence", "0%")
            try:
                conf = float(conf_str.strip('%')) / 100.0
                confidences.append(conf)
            except:
                pass
        
        if confidences:
            avg_confidence = sum(confidences) / len(confidences)
            report.append(f"\nAverage Confidence: {avg_confidence:.2%}")
        
        return "\n".join(report)
    
    def generate_detailed_report(self):
        """
        Generate detailed attendance report
        
        Returns:
            Formatted report string
        """
        report = []
        report.append("=" * 80)
        report.append("DETAILED ATTENDANCE REPORT")
        report.append("=" * 80)
        report.append(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        if not self.records:
            report.append("No attendance records found.\n")
        else:
            report.append(f"{'#':<3} {'Timestamp':<20} {'Name':<25} {'Reg#':<10} {'Status':<12} {'Conf':<6}")
            report.append("-" * 80)
            
            for i, record in enumerate(self.records, 1):
                timestamp = record.get("Timestamp", "")[:19]
                name = record.get("Student_Name", "Unknown")[:25]
                reg = record.get("Registration_Number", "N/A")[:10]
                status = record.get("Status", "unknown")[:12]
                conf = record.get("Confidence", "N/A")[:6]
                
                report.append(f"{i:<3} {timestamp:<20} {name:<25} {reg:<10} {status:<12} {conf:<6}")
        
        return "\n".join(report)
    
    def get_attendance_statistics(self):
        """
        Get attendance statistics
        
        Returns:
            Dictionary with statistics
        """
        total = len(self.records)
        
        if total == 0:
            return {
                "total_records": 0,
                "by_status": {},
                "by_method": {},
                "avg_confidence": 0.0
            }
        
        # Count by status
        by_status = {}
        for record in self.records:
            status = record.get("Status", "unknown")
            by_status[status] = by_status.get(status, 0) + 1
        
        # Count by method
        by_method = {}
        for record in self.records:
            method = record.get("Method", "unknown")
            by_method[method] = by_method.get(method, 0) + 1
        
        # Average confidence
        confidences = []
        for record in self.records:
            conf_str = record.get("Confidence", "0%")
            try:
                conf = float(conf_str.strip('%')) / 100.0
                confidences.append(conf)
            except:
                pass
        
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
        
        return {
            "total_records": total,
            "by_status": by_status,
            "by_method": by_method,
            "avg_confidence": avg_confidence
        }
    
    def export_report_to_file(self, report_type="summary", output_file=None):
        """
        Export report to text file
        
        Args:
            report_type: "summary" or "detailed"
            output_file: Output file path
            
        Returns:
            True if successful
        """
        try:
            if report_type == "summary":
                report = self.generate_summary_report()
            else:
                report = self.generate_detailed_report()
            
            if not output_file:
                date_str = datetime.now().strftime("%Y-%m-%d_%H%M%S")
                output_file = f"{self.log_dir}/report_{report_type}_{date_str}.txt"
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report)
            
            print(f"✓ Report exported to {output_file}")
            return True
            
        except Exception as e:
            print(f"✗ Export error: {e}")
            return False
    
    def load_previous_records(self):
        """Load previous records from CSV file"""
        try:
            if os.path.exists(self.log_file):
                with open(self.log_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    self.records = list(reader)
                print(f"✓ Loaded {len(self.records)} previous records")
        except Exception as e:
            print(f"✗ Error loading records: {e}")


def main():
    """Test attendance logger"""
    try:
        print("Testing Attendance Logger...\n")
        
        logger = AttendanceLogger()
        
        # Test logging
        print("Testing attendance logging...")
        
        student1 = {
            "Name": "Ahmed Ali",
            "Registration_Number": "REG001",
            "Email": "ahmed@uni.edu"
        }
        
        student2 = {
            "Name": "Fatima Khan",
            "Registration_Number": "REG002",
            "Email": "fatima@uni.edu"
        }
        
        logger.log_attendance(student1, status="admitted", confidence=0.95)
        logger.log_attendance(student2, status="admitted", confidence=0.92)
        
        print("✓ Students logged")
        
        # Generate report
        print("\nGenerating report...")
        report = logger.generate_summary_report()
        print(report)
        
        print("\n✓ Attendance logger test complete!")
        
    except Exception as e:
        print(f"✗ Test error: {e}")


if __name__ == "__main__":
    main()
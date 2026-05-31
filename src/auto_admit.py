"""
Auto-Admit Module for Zoom Attendance System
Handles automated right-click and admit button clicking
"""

import pyautogui
import time
from datetime import datetime
import json


class AutoAdmit:
    """Handles automatic admission of students"""
    
    def __init__(self, config=None):
        """
        Initialize auto-admit
        
        Args:
            config: Configuration dictionary with button positions
        """
        self.config = config or {}
        self.admitted_students = []
        self.failed_admits = []
        
        # Enable failsafe (move mouse to corner to stop)
        pyautogui.FAILSAFE = True
        
        # Add safety delay
        pyautogui.PAUSE = 0.1
    
    def move_to_position(self, x, y, duration=0.5):
        """
        Move mouse to position with safety checks
        
        Args:
            x: X coordinate
            y: Y coordinate
            duration: Time to move (seconds)
            
        Returns:
            True if successful
        """
        try:
            # Validate coordinates
            if x < 0 or y < 0:
                print(f"✗ Invalid coordinates: ({x}, {y})")
                return False
            
            # Move mouse
            pyautogui.moveTo(x, y, duration=duration)
            return True
            
        except Exception as e:
            print(f"✗ Mouse move error: {e}")
            return False
    
    def right_click(self, x, y, duration=0.3):
        """
        Right-click at position
        
        Args:
            x: X coordinate
            y: Y coordinate
            duration: Time to move before clicking
            
        Returns:
            True if successful
        """
        try:
            # Move to position
            if not self.move_to_position(x, y, duration):
                return False
            
            # Right-click
            pyautogui.rightClick()
            time.sleep(0.3)  # Wait for context menu
            
            return True
            
        except Exception as e:
            print(f"✗ Right-click error: {e}")
            return False
    
    def left_click(self, x, y, duration=0.3, clicks=1):
        """
        Left-click at position
        
        Args:
            x: X coordinate
            y: Y coordinate
            duration: Time to move before clicking
            clicks: Number of clicks
            
        Returns:
            True if successful
        """
        try:
            # Move to position
            if not self.move_to_position(x, y, duration):
                return False
            
            # Click
            pyautogui.click(clicks=clicks)
            time.sleep(0.2)  # Wait after click
            
            return True
            
        except Exception as e:
            print(f"✗ Left-click error: {e}")
            return False
    
    def find_and_click_button(self, button_position, button_text="Admit"):
        """
        Find and click admit button
        
        Args:
            button_position: (x, y) position of button
            button_text: Button text (for logging)
            
        Returns:
            True if successful
        """
        try:
            x, y = button_position
            
            # Move and click
            if self.left_click(x, y, duration=0.2):
                return True
            
            return False
            
        except Exception as e:
            print(f"✗ Button click error: {e}")
            return False
    
    def admit_student_by_right_click(self, student_name, student_position, admit_button_position):
        """
        Admit single student using right-click method
        
        Args:
            student_name: Student name (for logging)
            student_position: (x, y) position of student in waiting room
            admit_button_position: (x, y) position of admit button
            
        Returns:
            True if successful
        """
        try:
            print(f"\n  Admitting: {student_name}...")
            
            # Right-click on student
            if not self.right_click(student_position[0], student_position[1]):
                self.failed_admits.append({
                    "student": student_name,
                    "error": "Right-click failed",
                    "timestamp": datetime.now()
                })
                print(f"    ✗ Right-click failed")
                return False
            
            # Click admit button
            time.sleep(0.3)  # Wait for context menu
            
            if not self.left_click(admit_button_position[0], admit_button_position[1]):
                self.failed_admits.append({
                    "student": student_name,
                    "error": "Admit button click failed",
                    "timestamp": datetime.now()
                })
                print(f"    ✗ Admit button click failed")
                return False
            
            # Wait for admission
            time.sleep(0.5)
            
            # Log success
            self.admitted_students.append({
                "student": student_name,
                "method": "right_click",
                "timestamp": datetime.now()
            })
            
            print(f"    ✓ Admitted successfully")
            return True
            
        except Exception as e:
            print(f"    ✗ Admission error: {e}")
            self.failed_admits.append({
                "student": student_name,
                "error": str(e),
                "timestamp": datetime.now()
            })
            return False
    
    def admit_student_by_direct_click(self, student_name, admit_button_position):
        """
        Admit single student by directly clicking admit button
        (Used if right-click context menu not available)
        
        Args:
            student_name: Student name (for logging)
            admit_button_position: (x, y) position of admit button
            
        Returns:
            True if successful
        """
        try:
            print(f"\n  Admitting: {student_name}...")
            
            # Click admit button directly
            if not self.left_click(admit_button_position[0], admit_button_position[1]):
                self.failed_admits.append({
                    "student": student_name,
                    "error": "Direct click failed",
                    "timestamp": datetime.now()
                })
                print(f"    ✗ Click failed")
                return False
            
            # Wait for admission
            time.sleep(0.5)
            
            # Log success
            self.admitted_students.append({
                "student": student_name,
                "method": "direct_click",
                "timestamp": datetime.now()
            })
            
            print(f"    ✓ Admitted successfully")
            return True
            
        except Exception as e:
            print(f"    ✗ Admission error: {e}")
            self.failed_admits.append({
                "student": student_name,
                "error": str(e),
                "timestamp": datetime.now()
            })
            return False
    
    def admit_multiple_students(self, students_list, method="right_click"):
        """
        Admit multiple students
        
        Args:
            students_list: List of (name, position, button_position) tuples
            method: "right_click" or "direct_click"
            
        Returns:
            Tuple (admitted_count, failed_count)
        """
        print(f"\n▶ Starting auto-admit (method: {method})...")
        
        delay = self.config.get("delay_between_admits", 0.5)
        admitted_count = 0
        failed_count = 0
        
        for student_name, student_pos, button_pos in students_list:
            if method == "right_click":
                success = self.admit_student_by_right_click(
                    student_name, student_pos, button_pos
                )
            else:
                success = self.admit_student_by_direct_click(
                    student_name, button_pos
                )
            
            if success:
                admitted_count += 1
            else:
                failed_count += 1
            
            # Wait before next student
            time.sleep(delay)
        
        print(f"\n▶ Auto-admit complete:")
        print(f"  Admitted: {admitted_count}")
        print(f"  Failed: {failed_count}")
        
        return admitted_count, failed_count
    
    def test_mouse_position(self):
        """
        Test mouse position tracking
        Prints current position every 0.5 seconds for 5 seconds
        User can hover over elements to find coordinates
        """
        print("\n🧪 Testing mouse position tracking...")
        print("   Move mouse to elements to get coordinates")
        print("   Printing for 10 seconds...\n")
        
        start_time = time.time()
        
        try:
            while time.time() - start_time < 10:
                x, y = pyautogui.position()
                print(f"   Position: ({x}, {y})", end='\r')
                time.sleep(0.5)
            
            print("\n✓ Position tracking complete")
            
        except KeyboardInterrupt:
            print("\n⏹ Stopped")
    
    def verify_coordinates(self, x, y, pause_seconds=2):
        """
        Verify coordinates by moving mouse there
        
        Args:
            x: X coordinate
            y: Y coordinate
            pause_seconds: How long to show the position
        """
        print(f"\n🎯 Moving mouse to ({x}, {y})...")
        self.move_to_position(x, y)
        time.sleep(pause_seconds)
        print("✓ Returned to center")
    
    def get_statistics(self):
        """
        Get admission statistics
        
        Returns:
            Dictionary with statistics
        """
        total_admitted = len(self.admitted_students)
        total_failed = len(self.failed_admits)
        total_attempts = total_admitted + total_failed
        
        return {
            "total_admitted": total_admitted,
            "total_failed": total_failed,
            "total_attempts": total_attempts,
            "success_rate": (total_admitted / total_attempts * 100) if total_attempts > 0 else 0,
            "admitted_students": self.admitted_students,
            "failed_students": self.failed_admits
        }
    
    def generate_admit_report(self):
        """
        Generate admission report
        
        Returns:
            Formatted report string
        """
        stats = self.get_statistics()
        
        report = []
        report.append("=" * 70)
        report.append("AUTO-ADMIT REPORT")
        report.append("=" * 70)
        report.append(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        report.append(f"Total Attempts: {stats['total_attempts']}")
        report.append(f"Successfully Admitted: {stats['total_admitted']}")
        report.append(f"Failed: {stats['total_failed']}")
        report.append(f"Success Rate: {stats['success_rate']:.1f}%\n")
        
        if self.admitted_students:
            report.append("Admitted Students:")
            for student in self.admitted_students:
                ts = student['timestamp'].strftime('%H:%M:%S')
                report.append(f"  ✓ {student['student']} ({ts})")
        
        if self.failed_admits:
            report.append("\nFailed Admissions:")
            for student in self.failed_admits:
                ts = student['timestamp'].strftime('%H:%M:%S')
                report.append(f"  ✗ {student['student']}: {student['error']} ({ts})")
        
        return "\n".join(report)
    
    def reset_statistics(self):
        """Reset admission statistics"""
        self.admitted_students = []
        self.failed_admits = []


def main():
    """Test auto-admit module"""
    try:
        print("Testing Auto-Admit Module...\n")
        
        admit = AutoAdmit()
        
        # Test position tracking
        print("Test 1: Mouse Position Tracking")
        admit.test_mouse_position()
        
        print("\n✓ Auto-admit test complete!")
        
    except Exception as e:
        print(f"✗ Test error: {e}")


if __name__ == "__main__":
    main()
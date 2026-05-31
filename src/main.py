"""
Main Program for Zoom Attendance Auto-Capture System
Coordinates screen capture and attendance tracking
"""

import sys
import os
from datetime import datetime
import json
import csv

# Import screen capture module
from screen_capture import ScreenCapture


class AttendanceSystem:
    """Main attendance system coordinator"""
    
    def __init__(self):
        """Initialize attendance system"""
        self.config = None
        self.capture = None
        self.log_file = None
        self.frame_count = 0
        self.start_time = None
        
    def setup(self):
        """
        Setup system: load config, create directories, prepare logging
        
        Returns:
            True if setup successful, False otherwise
        """
        try:
            print("=" * 60)
            print("  ZOOM ATTENDANCE AUTO-CAPTURE SYSTEM")
            print("=" * 60)
            print("\n⚙️  Setting up system...\n")
            
            # Load configuration
            print("1️⃣  Loading configuration...")
            if not os.path.exists("config/settings.json"):
                print("   ✗ config/settings.json not found!")
                return False
            
            # Initialize screen capture
            print("2️⃣  Initializing screen capture...")
            self.capture = ScreenCapture("config/settings.json")
            self.config = self.capture.config
            
            # Create log file
            print("3️⃣  Preparing attendance log...")
            self.setup_log_file()
            
            # Validate coordinates
            print("4️⃣  Validating configuration...")
            if not self.validate_config():
                print("   ✗ Configuration validation failed!")
                return False
            
            print("\n✓ System setup complete!\n")
            return True
            
        except Exception as e:
            print(f"✗ Setup error: {e}")
            return False
    
    def validate_config(self):
        """
        Validate configuration values
        
        Returns:
            True if valid, False otherwise
        """
        try:
            required_keys = ["capture_interval", "waiting_room_region"]
            
            for key in required_keys:
                if key not in self.config:
                    print(f"   ✗ Missing config key: {key}")
                    return False
            
            # Check region coordinates
            region = self.config["waiting_room_region"]
            if not all(k in region for k in ["x", "y", "width", "height"]):
                print("   ✗ Invalid waiting_room_region coordinates")
                return False
            
            print(f"   ✓ Capture interval: {self.config['capture_interval']}s")
            print(f"   ✓ Region: ({region['x']}, {region['y']}) - {region['width']}x{region['height']}")
            
            return True
            
        except Exception as e:
            print(f"   ✗ Validation error: {e}")
            return False
    
    def setup_log_file(self):
        """Setup attendance log file"""
        try:
            # Create logs directory if not exists
            if not os.path.exists("logs"):
                os.makedirs("logs")
            
            # Create log filename with date
            date_str = datetime.now().strftime("%Y-%m-%d")
            self.log_file = f"logs/attendance_{date_str}.csv"
            
            # Create header if file doesn't exist
            if not os.path.exists(self.log_file):
                with open(self.log_file, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow([
                        "Timestamp",
                        "Frame_Number",
                        "Status",
                        "Details"
                    ])
                print(f"   ✓ Created log file: {self.log_file}")
            else:
                print(f"   ✓ Using existing log file: {self.log_file}")
            
        except Exception as e:
            print(f"   ✗ Log file error: {e}")
            self.log_file = None
    
    def log_message(self, message, frame_number=0, status="INFO"):
        """
        Log message to file and console
        
        Args:
            message: Message to log
            frame_number: Frame number
            status: Status type (INFO, CAPTURE, ERROR, etc.)
        """
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
            
            # Log to file
            if self.log_file:
                with open(self.log_file, 'a', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow([timestamp, frame_number, status, message])
            
            # Print to console
            print(f"  [{timestamp}] {status}: {message}")
            
        except Exception as e:
            print(f"  Error logging: {e}")
    
    def process_frame(self, result):
        """
        Process captured frame (callback function)
        
        Args:
            result: Dictionary with captured image and metadata
        """
        try:
            if result is None:
                return
            
            frame_number = result.get("frame_count", 0)
            timestamp = result.get("timestamp")
            
            # Get image dimensions
            height = result.get("height", 0)
            width = result.get("width", 0)
            
            # Log frame capture
            details = f"Size: {width}x{height}px"
            self.log_message(details, frame_number, "CAPTURE")
            
            # Update counter
            self.frame_count = frame_number
            
        except Exception as e:
            self.log_message(f"Frame processing error: {e}", 0, "ERROR")
    
    def display_summary(self):
        """Display system summary after capture"""
        print("\n" + "=" * 60)
        print("  CAPTURE SUMMARY")
        print("=" * 60)
        
        elapsed = datetime.now() - self.start_time if self.start_time else None
        
        print(f"\n📊 Statistics:")
        print(f"   Total frames captured: {self.frame_count}")
        if elapsed:
            print(f"   Duration: {elapsed}")
            avg_fps = self.frame_count / elapsed.total_seconds() if elapsed.total_seconds() > 0 else 0
            print(f"   Average FPS: {avg_fps:.2f}")
        print(f"   Log file: {self.log_file}")
        
        print("\n✓ System shutdown complete\n")
    
    def run(self):
        """
        Run the attendance system
        Main capture loop
        """
        try:
            # Setup
            if not self.setup():
                print("\n✗ Setup failed. Exiting...")
                return False
            
            # Show instructions
            print("📋 Instructions:")
            print("   1. Start Zoom meeting")
            print("   2. Ensure students are in waiting room")
            print("   3. Program will capture and log activity")
            print("   4. Press Ctrl+C to stop\n")
            
            input("Press Enter to start screen capture...\n")
            
            # Start capture
            self.start_time = datetime.now()
            print("▶ Screen capture starting...\n")
            
            # Run continuous capture
            self.capture.continuous_capture(
                callback=self.process_frame,
                duration=None,  # Run indefinitely
                save_screenshots=False,  # Set True to save all screenshots
                display=False  # Set True to display frames
            )
            
            # Display summary
            self.display_summary()
            
            return True
            
        except KeyboardInterrupt:
            print("\n\n⏹ Capture interrupted by user")
            self.display_summary()
            return True
        except Exception as e:
            print(f"\n✗ Fatal error: {e}")
            return False
    
    def test_capture(self):
        """Test screen capture without full system"""
        try:
            print("\n🧪 Testing screen capture...\n")
            
            if not os.path.exists("config/settings.json"):
                print("✗ config/settings.json not found!")
                return
            
            self.capture = ScreenCapture("config/settings.json")
            
            # Test single capture
            print("Capturing single frame...")
            result = self.capture.capture_and_process(save=True, display=False)
            
            if result:
                print(f"✓ Capture successful!")
                print(f"  Image size: {result['width']}x{result['height']}")
                print(f"  Saved to: {result.get('filename', 'N/A')}")
            else:
                print("✗ Capture failed!")
            
        except Exception as e:
            print(f"✗ Test error: {e}")


def main():
    """
    Main entry point
    """
    try:
        # Check for command line arguments
        if len(sys.argv) > 1:
            if sys.argv[1] == "--test":
                # Test mode
                system = AttendanceSystem()
                system.test_capture()
                return
            elif sys.argv[1] == "--help":
                print("""
Zoom Attendance Auto-Capture System

Usage:
    python main.py              - Run attendance system
    python main.py --test       - Test screen capture
    python main.py --help       - Show this help

Before running:
    1. Create config/settings.json with Zoom coordinates
    2. Create config/students.csv or data/students.csv with student list
    3. Ensure config/ and logs/ directories exist

Requirements:
    - config/settings.json     - Configuration file
    - Python 3.7+
    - All dependencies installed (pip install -r requirements.txt)
                """)
                return
        
        # Normal mode - run system
        system = AttendanceSystem()
        success = system.run()
        
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n\nProgram interrupted")
        sys.exit(0)
    except Exception as e:
        print(f"\nFatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
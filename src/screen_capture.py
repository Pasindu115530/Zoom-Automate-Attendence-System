"""
Screen Capture Module for Zoom Attendance System
Handles screen capture, cropping, preprocessing, and storage
"""

import mss
import cv2
import numpy as np
import json
import os
from datetime import datetime
import time


class ScreenCapture:
    """Handles all screen capture operations"""
    
    def __init__(self, config_path="config/settings.json"):
        """
        Initialize screen capture with configuration
        
        Args:
            config_path: Path to configuration JSON file
        """
        self.config = self.load_config(config_path)
        self.mss = mss.mss()
        self.screenshots_dir = "screenshots"
        self.create_directories()
        
    def load_config(self, config_path):
        """
        Load configuration from JSON file
        
        Args:
            config_path: Path to settings.json
            
        Returns:
            Dictionary with configuration settings
        """
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            print(f"✓ Configuration loaded from {config_path}")
            return config
        except FileNotFoundError:
            print(f"✗ Configuration file not found: {config_path}")
            raise
        except json.JSONDecodeError:
            print(f"✗ Configuration file is not valid JSON: {config_path}")
            raise
    
    def create_directories(self):
        """Create necessary directories if they don't exist"""
        if not os.path.exists(self.screenshots_dir):
            os.makedirs(self.screenshots_dir)
            print(f"✓ Created directory: {self.screenshots_dir}")
        
        if not os.path.exists("logs"):
            os.makedirs("logs")
            print(f"✓ Created directory: logs")
    
    def capture_screen(self, use_full_screen=False):
        """
        Capture screen or specific region
        
        Args:
            use_full_screen: If True, capture entire screen. If False, use waiting_room_region
            
        Returns:
            Captured image as numpy array (BGR format)
        """
        try:
            if use_full_screen:
                # Capture full screen
                monitor = self.mss.monitors[1]  # Primary monitor
                screenshot = self.mss.grab(monitor)
            else:
                # Capture only waiting room region
                region = self.config.get("waiting_room_region")
                if not region:
                    raise ValueError("waiting_room_region not defined in config")
                
                monitor = {
                    "left": region["x"],
                    "top": region["y"],
                    "width": region["width"],
                    "height": region["height"]
                }
                screenshot = self.mss.grab(monitor)
            
            # Convert to numpy array (BGR format for OpenCV)
            image = np.array(screenshot)
            # MSS returns RGBA, convert to BGR for OpenCV
            image = cv2.cvtColor(image, cv2.COLOR_RGBA2BGR)
            
            return image
            
        except Exception as e:
            print(f"✗ Error capturing screen: {e}")
            return None
    
    def crop_region(self, image, region_coords):
        """
        Crop a specific region from image
        
        Args:
            image: Source image (numpy array)
            region_coords: Dictionary with x, y, width, height
            
        Returns:
            Cropped image
        """
        try:
            if image is None:
                return None
            
            x = region_coords["x"]
            y = region_coords["y"]
            width = region_coords["width"]
            height = region_coords["height"]
            
            # Crop: image[y:y+height, x:x+width]
            cropped = image[y:y+height, x:x+width]
            
            return cropped
            
        except Exception as e:
            print(f"✗ Error cropping region: {e}")
            return None
    
    def preprocess_image(self, image):
        """
        Preprocess image for better OCR accuracy
        
        Args:
            image: Input image (numpy array)
            
        Returns:
            Preprocessed image
        """
        try:
            if image is None:
                return None
            
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Increase contrast using CLAHE (Contrast Limited Adaptive Histogram Equalization)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            enhanced = clahe.apply(gray)
            
            # Denoise
            denoised = cv2.fastNlMeansDenoising(enhanced)
            
            return denoised
            
        except Exception as e:
            print(f"✗ Error preprocessing image: {e}")
            return None
    
    def save_screenshot(self, image, label="capture"):
        """
        Save screenshot to disk
        
        Args:
            image: Image to save (numpy array)
            label: Label for filename
            
        Returns:
            Filename if successful, None otherwise
        """
        try:
            if image is None:
                return None
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
            filename = f"{self.screenshots_dir}/{label}_{timestamp}.png"
            
            cv2.imwrite(filename, image)
            return filename
            
        except Exception as e:
            print(f"✗ Error saving screenshot: {e}")
            return None
    
    def display_image(self, image, title="Screen Capture", wait_ms=1):
        """
        Display image in window (for debugging)
        
        Args:
            image: Image to display
            title: Window title
            wait_ms: How long to display (ms). 0 = wait for key press
        """
        if image is None:
            return
        
        cv2.imshow(title, image)
        cv2.waitKey(wait_ms)
    
    def add_text_to_image(self, image, text, position=(10, 30)):
        """
        Add text overlay to image
        
        Args:
            image: Image to modify
            text: Text to add
            position: (x, y) position for text
            
        Returns:
            Image with text overlay
        """
        if image is None:
            return None
        
        try:
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.7
            color = (0, 255, 0)  # Green in BGR
            thickness = 2
            
            cv2.putText(image, text, position, font, font_scale, color, thickness)
            return image
            
        except Exception as e:
            print(f"✗ Error adding text: {e}")
            return image
    
    def capture_and_process(self, save=False, display=False):
        """
        Complete capture and process pipeline
        
        Args:
            save: If True, save captured image to disk
            display: If True, display image on screen
            
        Returns:
            Dictionary with captured image and metadata
        """
        try:
            # Capture screen
            raw_image = self.capture_screen(use_full_screen=False)
            if raw_image is None:
                return None
            
            # Preprocess for better quality
            processed_image = self.preprocess_image(raw_image)
            
            # Get timestamp
            timestamp = datetime.now()
            
            # Create result dictionary
            result = {
                "timestamp": timestamp,
                "raw_image": raw_image,
                "processed_image": processed_image,
                "width": raw_image.shape[1],
                "height": raw_image.shape[0]
            }
            
            # Optionally save
            if save:
                filename = self.save_screenshot(raw_image, "waiting_room")
                result["filename"] = filename
            
            # Optionally display
            if display:
                display_image = self.add_text_to_image(
                    processed_image.copy(),
                    f"Captured: {timestamp.strftime('%H:%M:%S.%f')[:-3]}"
                )
                self.display_image(display_image, "Waiting Room")
            
            return result
            
        except Exception as e:
            print(f"✗ Error in capture_and_process: {e}")
            return None
    
    def continuous_capture(self, callback=None, duration=None, save_screenshots=False, display=False):
        """
        Continuously capture screen at intervals
        
        Args:
            callback: Function to call with each captured frame
            duration: How long to run (seconds). None = infinite
            save_screenshots: If True, save each frame to disk
            display: If True, display each frame
        """
        print("▶ Starting continuous screen capture...")
        print(f"  Interval: {self.config.get('capture_interval', 1.5)} seconds")
        
        start_time = time.time()
        frame_count = 0
        
        try:
            while True:
                frame_count += 1
                
                # Check duration
                if duration:
                    elapsed = time.time() - start_time
                    if elapsed > duration:
                        print(f"▶ Duration complete ({duration}s). Stopping...")
                        break
                
                # Capture and process
                result = self.capture_and_process(
                    save=save_screenshots,
                    display=display
                )
                
                if result:
                    result["frame_count"] = frame_count
                    
                    # Call callback if provided
                    if callback:
                        callback(result)
                    else:
                        # Default: just print status
                        print(f"  Frame {frame_count}: {result['timestamp'].strftime('%H:%M:%S.%f')[:-3]}")
                
                # Wait for interval
                interval = self.config.get("capture_interval", 1.5)
                time.sleep(interval)
        
        except KeyboardInterrupt:
            print(f"\n⏹ Screen capture stopped by user (after {frame_count} frames)")
        except Exception as e:
            print(f"✗ Error during continuous capture: {e}")
        finally:
            cv2.destroyAllWindows()
            print("▶ Closing screen capture...")


def main():
    """Test screen capture module"""
    try:
        # Initialize capture
        capture = ScreenCapture()
        
        # Capture 5 frames as test
        print("\nTesting screen capture (5 frames)...")
        
        def test_callback(result):
            print(f"  ✓ Frame {result['frame_count']}: {result['timestamp'].strftime('%H:%M:%S')}")
        
        capture.continuous_capture(callback=test_callback, duration=10, save_screenshots=True, display=False)
        
        print("\n✓ Screen capture test complete!")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")


if __name__ == "__main__":
    main()
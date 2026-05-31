# Zoom Attendance Auto-Capture System

A Python-based automation system that automatically captures the Zoom waiting room, recognizes student names and registration numbers using OCR, and auto-admits registered students.

---

## 📋 Features

- ✅ **Auto Screen Capture** - Continuously captures Zoom waiting room
- ✅ **OCR Text Recognition** - Extracts student names and registration numbers
- ✅ **Student Matching** - Matches captured names with database
- ✅ **Auto-Admit** - Automatically right-clicks and admits registered students
- ✅ **Attendance Logging** - Records all admitted students with timestamps
- ✅ **Configurable Settings** - Easy customization via JSON config
- ✅ **Error Handling** - Graceful error management and logging

---

## 🔧 Requirements

### Software Requirements
- **Python 3.7 or higher**
- **Windows/Mac/Linux**
- **Tesseract OCR** (installed separately)
- **Zoom** (running with waiting room enabled)

### Hardware Recommendations
- **Processor**: Intel i5 or equivalent
- **RAM**: 4GB minimum
- **Screen Resolution**: 1920x1080 or higher

---

## 📦 Installation

### Step 1: Install Python
Download and install Python 3.7+ from [python.org](https://www.python.org)

### Step 2: Install Tesseract OCR

**Windows:**
1. Download installer from: https://github.com/UB-Mannheim/tesseract/wiki
2. Run installer and note installation path (usually `C:\Program Files\Tesseract-OCR`)
3. Add to `config/settings.json`:
```json
"tesseract_path": "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
```

**Mac:**
```bash
brew install tesseract
```

**Linux:**
```bash
sudo apt-get install tesseract-ocr
```

### Step 3: Create Project Folder
```bash
mkdir zoom-attendance-system
cd zoom-attendance-system
```

### Step 4: Create Folder Structure
```bash
mkdir config data logs screenshots src
```

### Step 5: Install Python Dependencies
```bash
pip install -r requirements.txt
```

---

## 📁 File Structure

```
zoom-attendance-system/
│
├── config/
│   ├── settings.json          # Main configuration file
│   └── students.csv           # Student database
│
├── data/
│   └── students.csv           # Student list (backup)
│
├── logs/
│   └── attendance_YYYY-MM-DD.csv  # Auto-generated attendance records
│
├── screenshots/
│   └── (auto-created temporary captures)
│
├── src/
│   ├── screen_capture.py      # Screen capture module
│   ├── ocr_processor.py       # OCR text extraction
│   ├── student_matcher.py     # Student database matching
│   ├── auto_admit.py          # Auto-click admit button
│   ├── attendance_logger.py   # Attendance recording
│   └── main.py                # Main program
│
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

---

## ⚙️ Configuration

### 1. Create `config/settings.json`

Edit and set your screen coordinates:

```json
{
  "capture_interval": 1.5,
  "zoom_window": {
    "x": 0,
    "y": 0,
    "width": 1920,
    "height": 1080
  },
  "waiting_room_region": {
    "x": 500,
    "y": 100,
    "width": 600,
    "height": 700
  },
  "admit_button_offset": {
    "x": 50,
    "y": 0
  },
  "tesseract_path": "C:\\Program Files\\Tesseract-OCR\\tesseract.exe",
  "min_confidence": 0.7,
  "name_match_threshold": 0.85,
  "delay_between_admits": 0.5
}
```

**How to find coordinates:**
1. Open Zoom waiting room
2. Hover your mouse over the waiting room list area
3. Note the x, y coordinates (use tools like `print(pyautogui.position())`)
4. Calculate width and height of the region

### 2. Create `config/students.csv` or `data/students.csv`

Add your student list:

```csv
Name,Registration_Number,Email,Status
Ahmed Ali,REG001,ahmed@uni.edu,active
Fatima Khan,REG002,fatima@uni.edu,active
Hassan Mohamed,REG003,hassan@uni.edu,active
Layla Ahmed,REG004,layla@uni.edu,active
Sara Ibrahim,REG005,sara@uni.edu,active
```

---

## 🚀 How to Run

### Step 1: Prepare Zoom
1. Start Zoom meeting
2. Enable waiting room settings
3. Have students join and wait in waiting room

### Step 2: Run the Program
```bash
python src/main.py
```

### Step 3: Monitor Progress
- Watch console output for captured students
- Check `logs/` folder for attendance records
- Screenshots stored in `screenshots/` (temporary)

### Step 4: Stop Program
Press `Ctrl+C` to stop

---

## 📊 Output Files

### Attendance Log: `logs/attendance_YYYY-MM-DD.csv`

```csv
Timestamp,Student_Name,Registration_Number,Status,Confidence
2024-05-31 10:15:23,Ahmed Ali,REG001,admitted,0.95
2024-05-31 10:15:45,Fatima Khan,REG002,admitted,0.92
2024-05-31 10:16:12,Hassan Mohamed,REG003,admitted,0.88
```

### Summary Report

After running, generates:
- Total students admitted
- List of missing students
- Timestamps for each admission
- OCR confidence scores

---

## 🔍 Key Files Explained

### `src/main.py`
Main program that:
- Loads configuration
- Starts capture loop
- Coordinates all modules
- Handles program lifecycle

### `src/screen_capture.py`
Handles:
- Screen region capture
- Image preprocessing
- Frame rate management
- Saving screenshots

### `src/ocr_processor.py`
Performs:
- Text extraction via Tesseract
- Text cleaning and parsing
- Extraction of names and registration numbers
- Confidence scoring

### `src/student_matcher.py`
Manages:
- Loading student database
- Matching OCR text with database
- Fuzzy matching for typos
- Confidence calculation

### `src/auto_admit.py`
Controls:
- Mouse positioning
- Right-click actions
- Button clicking
- Timing and delays

### `src/attendance_logger.py`
Records:
- Admission timestamps
- Student details
- Confidence scores
- Status updates

---

## ⚠️ Important Notes

### Safety & Ethics
- **Only use on your own meetings** where you have permission
- **Get consent** from institution before deploying
- **Follow FERPA/GDPR** regulations for student data
- **Keep logs secure** - contains student information
- **Review before deployment** to educational network

### Performance
- Adjust `capture_interval` if CPU usage is high
- Increase interval for slower computers (1.5 → 2.5 seconds)
- Decrease for faster response (1.5 → 1.0 seconds)
- Monitor RAM usage with continuous operation

### Zoom Interface Changes
- Settings may change with Zoom updates
- Verify coordinates match your Zoom version
- Button positions might differ by resolution
- Test thoroughly before live use

---

## 🐛 Troubleshooting

### Problem: "Tesseract not found"
**Solution:**
- Install Tesseract OCR (see Installation section)
- Verify path in `config/settings.json`
- Restart Python after installing

### Problem: "OCR reading incorrect names"
**Solution:**
- Zoom in on waiting room area
- Improve screenshot quality (brightness, contrast)
- Increase `capture_interval` for clearer images
- Verify Tesseract installation

### Problem: "Auto-admit not clicking button"
**Solution:**
- Verify button coordinates in settings
- Check if Zoom window is in focus
- Test coordinates using `pyautogui.position()`
- Add screenshots to verify detection

### Problem: "Script runs slowly"
**Solution:**
- Increase `capture_interval` (1.5 → 2.0 seconds)
- Reduce waiting room region size
- Close other applications
- Check CPU/RAM usage

### Problem: "Students not matching database"
**Solution:**
- Check spelling in `students.csv`
- Verify OCR is reading names correctly
- Lower `name_match_threshold` if needed (0.85 → 0.80)
- Check for special characters in names

### Problem: "Log file not created"
**Solution:**
- Verify `logs/` folder exists
- Check write permissions on folder
- Ensure program ran without errors
- Check console output for errors

---

## 📈 Usage Tips

1. **Test with small group first** - Start with 2-3 students
2. **Verify coordinates** - Take screenshots and check accuracy
3. **Monitor first run** - Watch to ensure correct behavior
4. **Adjust delays** - Increase timing if auto-admit is too fast
5. **Keep logs** - Archive attendance records for verification
6. **Update database** - Keep student list current

---

## 🔐 Data Security

- Student data stored locally only
- No cloud uploads
- Delete logs when no longer needed
- Keep backup of student database
- Use file permissions to restrict access
- Consider encrypting attendance logs

---

## 📝 Requirements.txt Content

```
mss==1.9.1
pytesseract==0.3.10
opencv-python==4.8.0
pyautogui==0.9.53
pillow==10.0.0
fuzzywuzzy==0.18.0
python-levenshtein==0.21.1
pandas==2.0.0
```

Create file `requirements.txt` and paste above content, then run:
```bash
pip install -r requirements.txt
```

---

## 🆘 Getting Help

If you encounter issues:

1. **Check console output** - Look for error messages
2. **Review troubleshooting** - See section above
3. **Verify configuration** - Double-check settings.json
4. **Test components separately** - Run each module independently
5. **Check logs** - Review attendance_YYYY-MM-DD.csv for clues

---

## 📅 Maintenance

### Regular Tasks
- Delete old screenshot files weekly
- Archive attendance logs monthly
- Update student database each semester
- Verify coordinates if Zoom updates
- Check Tesseract installation

### Before Each Use
- Verify settings.json coordinates are correct
- Confirm student database is current
- Test with 1-2 students first
- Check that Zoom waiting room is enabled

---

## 🎯 Next Steps

1. ✅ Create folder structure
2. ✅ Install Python and dependencies
3. ✅ Create configuration files
4. ✅ Create student database
5. ✅ Create Python source files
6. ✅ Test with small group
7. ✅ Deploy to live meeting

---

## 📞 Support

For questions or issues:
- Review this README thoroughly
- Check troubleshooting section
- Test with simple scripts first
- Verify all dependencies installed
- Check Python version (3.7+)

---

## ⚖️ Legal Notice

This tool is provided for educational purposes. Users are responsible for:
- Complying with institutional policies
- Obtaining necessary permissions
- Following data protection regulations
- Respecting student privacy
- Using within legal boundaries

---

**Version:** 1.0  
**Last Updated:** May 2024  
**Tested on:** Python 3.8+, Zoom 5.x+

---

## Quick Command Reference

```bash
# Install dependencies
pip install -r requirements.txt

# Run the program
python src/main.py

# Stop program
Ctrl+C

# View logs
cat logs/attendance_2024-05-31.csv

# Test screen capture
python -c "from mss import mss; import time; m = mss.mss(); time.sleep(2); m.grab((500, 100, 1100, 800))"

# Check Python version
python --version

# Check Tesseract installation
tesseract --version
```

---

**Ready to start? Follow the Installation section above!** 🚀

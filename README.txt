📸 Screen capture using PIL.ImageGrab

🔍 OCR via EasyOCR

🧮 Expression parsing and solving using SymPy

🖱️ Automated mouse input with PyAutoGUI

🟥 Transparent OCR region overlay

🟦 Visual keypad coordinate overlays

🪟 Mouse clicks pass through overlays (Windows only)

📦 Requirements

Python 3.9+

pip

Supported OS (see table above)

🪟 Windows Setup (Recommended)
1️⃣ Install Python

Download Python from the official website
During installation, check:

☑ Add Python to PATH


Verify:

python --version

2️⃣ Install dependencies

In the project directory:

pip install easyocr pillow pyautogui numpy sympy opencv-python

3️⃣ Run the program
python main.py


Replace main.py with the actual filename if different.

4️⃣ Expected behaviour

Red box → OCR capture area

Cyan boxes → keypad button locations

Overlays are always on top

Mouse clicks pass through overlays

Terminal logs detected expressions and actions

🍎 macOS Setup (Limited Support)
1️⃣ Install Python
brew install python


Verify:

python3 --version

2️⃣ Install dependencies
pip3 install easyocr pillow pyautogui numpy sympy opencv-python

3️⃣ Grant permissions

Go to:

System Settings → Privacy & Security


Enable:

Screen Recording → Terminal / IDE

Accessibility → Terminal / IDE

Restart Terminal after enabling permissions.

⚠️ macOS Limitations

Transparent overlays are not supported

ctypes.windll is Windows-only

OCR, solving, and logic still function

Auto-clicking depends on accessibility permissions

macOS users may comment out setup_overlay_boxes() for stability.

⚙️ Configuration
OCR Capture Area
QUESTION_AREA = (410, 182, 711, 227)


Format:

(x1, y1, x2, y2)


Adjust this to match where questions appear on your screen.

Keypad Coordinates
KEY_COORDS = {
    '0': (486, 613),
    '1': (464, 537),
    ...
}


Coordinates must match:

Screen resolution

Application layout

Display scaling (Windows DPI)

🧪 How It Works (Pipeline)

Capture OCR region

Convert image to grayscale

Apply thresholding

OCR text detection

Normalise operators (×, ÷, etc.)

Fix missing operators

Solve expression

Click digits + OK button

🧯 Troubleshooting

OCR results are inaccurate

Increase text size

Improve contrast

Adjust threshold value:

img.point(lambda x: 0 if x < 140 else 255)


Incorrect clicks

Verify KEY_COORDS

Disable display scaling

Ensure resolution matches setup

Windows overlay issues

Run as administrator

Disable DPI scaling

Ensure Python is not sandboxed

📝 Notes

Screen coordinates are environment-specific

This project is intended for educational and experimental use

Logic and overlays are modular and can be extended
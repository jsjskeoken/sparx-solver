🧮 Sparx Maths Auto-Solver (specifically for times tables can automate 100 club check)

A high-performance, Python-based automation tool designed to visually read, solve, and answer math questions on screen. It utilizes Optical Character Recognition (OCR) to detect equations and simulates mouse input to answer them instantly.

New Feature: This version includes a built-in XP Farming mode that automatically navigates through menus after completing sets of questions.

⚠️ Disclaimer: This software is for educational and experimental purposes only. Using automation tools may violate the terms of service of educational platforms. Use responsibly.

✨ Features

📸 Instant Screen Capture: Uses PIL.ImageGrab for low-latency screen reading.

🔍 AI-Powered OCR: Integrated EasyOCR (GPU-accelerated) to read mathematical expressions.

🧮 Symbolic Math Engine: Uses SymPy to parse and solve complex algebraic equations.

🖱️ Auto-Input: Simulates human mouse movements and clicks via PyAutoGUI.

🌾 XP Farming / AFK Mode:

Automatically clicks "Continue" (Yellow box) after every 10 correct answers.

Triggers a full menu navigation sequence (Magenta & Lime boxes) after every 3 sets (30 questions) to restart games or claim rewards.

🖥️ Transparent Overlays:

Red Box: Visualizes the OCR scan area.

Cyan Boxes: Shows keypad button locations.

Color-Coded Auto Boxes: Shows automation click targets (Yellow, Magenta, Lime).

Click-Through: Overlays do not interfere with mouse interaction (Windows only).

🛠️ Requirements

OS: Windows 10/11 (Highly Recommended).

macOS is supported but has limitations with transparent overlays.

Python: Version 3.9 or higher.

📥 Installation

1️⃣ Windows Setup (Recommended)

Install Python

Download from python.org.

Crucial: Check the box "Add Python to PATH" during installation.

Clone or Download this Repository

Extract the files to a folder on your desktop.

Install Dependencies
Open a terminal (Command Prompt or PowerShell) in the project folder and run:

pip install -r requirements.txt


(If you don't have the text file, run: pip install easyocr pillow pyautogui numpy sympy opencv-python pynput)

Run the Bot

python yep.py


2️⃣ macOS Setup (Experimental)

Install Python via Homebrew

brew install python


Install Dependencies

pip3 install -r requirements.txt


Grant Permissions (Critical)

Go to System Settings > Privacy & Security.

Enable Screen Recording for your Terminal/IDE.

Enable Accessibility for your Terminal/IDE.

Restart your terminal after changing these settings.

macOS Limitations: ctypes (used for transparent overlays) is Windows-only. You may need to comment out setup_overlay_boxes() in yep.py if it crashes.

⚙️ Configuration & Coordinate Setup

Since every monitor has a different resolution and scaling, you must configure the coordinates before the bot will work correctly.

Step 1: Use the Coordinate Logger

I have included a helper script called logger.py.

Run the logger:

python logger.py


Keypad: Hover over each number (0-9 and OK) and note the coordinates shown in the terminal.

Question Area: Note the Top-Left and Bottom-Right corners of the question text.

Automation Areas: Hover over the following buttons to set up the auto-clicker:

Auto Area 1 (Yellow): The primary "Continue" button (clicked after 10 answers).

Auto Area 2 (Magenta): The second button in the navigation sequence (e.g., "Menu" or "Games").

Auto Area 3 (Lime): The third button in the sequence (e.g., "Select Game").

Step 2: Update yep.py

Open yep.py in a text editor and update the ORIGINAL_QUESTION_AREA and ORIGINAL_KEY_COORDS, plus the new ORIGINAL_AUTO_AREA variables with the numbers you found:

# (x1, y1, x2, y2) - TopLeft X, TopLeft Y, BottomRight X, BottomRight Y
ORIGINAL_QUESTION_AREA = (411, 182, 722, 231) 

ORIGINAL_KEY_COORDS = {
    '0': (486, 613), 
    '1': (464, 537), 
    # ... update all numbers ...
    'OK': (689, 576)
}

# Automation Click Targets
ORIGINAL_AUTO_AREA_1 = (510, 686)  # First click (Yellow)
ORIGINAL_AUTO_AREA_2 = (157, 745)  # Second click (Magenta)
ORIGINAL_AUTO_AREA_3 = (274, 430)  # Third click (Lime)


🎮 How to Use

Once configured and running, the bot works in the background.

Key

Action

F9

Pause / Resume the bot.

F10

Toggle Overlays (Show/Hide the red, cyan, and auto boxes).

F11

Switch Mode (Toggles between "Club" mode and "Games" mode).

Ctrl+C

Force Quit (in the terminal).

🤖 Automation Logic (The "Loop")

The bot tracks your progress and automatically performs menu clicks:

Answer Tracking: It counts every correct answer provided.

The 10-Answer Trigger: After 10 answers, it waits 1 second and clicks Auto Area 1 (Yellow).

The 3-Set Trigger: Once the 10-answer trigger happens 3 times (30 total questions), it performs a full reset sequence:

Waits 10 seconds -> Clicks Auto Area 2 (Magenta).

Waits 2 seconds -> Clicks Auto Area 3 (Lime).

Waits 8 seconds -> Clicks Auto Area 1 (Yellow) to restart.

❓ Troubleshooting

📉 OCR is reading wrong numbers

Contrast: Ensure the background of the question is not too similar to the text color.

Threshold: You can adjust the image processing line in main_loop:

# Increase or decrease 140 to change darkness sensitivity
img_array[img_array < 140] = 0 


🖱️ Mouse is clicking the wrong spots

Display Scaling: Windows Display Scaling (125%, 150%) often breaks coordinate systems.

Fix: Set your Display Scale to 100% in Windows Settings.

Fix: Or, re-run logger.py while your scaling is active.

Resolution: Ensure the browser window is maximized and in the same position every time.

🪟 Overlays are black or not transparent

Ensure you are running on Windows.

Try running the terminal as Administrator.

Ensure your terminal/IDE is using the correct python environment.

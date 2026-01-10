Features

📸 Screen capture using PIL.ImageGrab

🔍 OCR via EasyOCR

🧮 Expression parsing and solving using SymPy

🖱️ Automated mouse input with PyAutoGUI

🟥 Transparent OCR region overlay

🟦 Visual keypad coordinate overlays

🪟 Mouse clicks pass through overlays (Windows only)

Requirements

Python 3.9+

pip package manager

Supported OS: Windows (recommended), macOS (limited support)

Installation
1️⃣ Windows Setup (Recommended)

Install Python

Download Python from the official website

During installation, check “Add Python to PATH”

Verify installation:

python --version

Install dependencies
Open a terminal in the project directory and run:

pip install easyocr pillow pyautogui numpy sympy opencv-python

Run the program

python main.py

Replace main.py with the actual filename if different.

Expected behaviour

Red box → OCR capture area

Cyan boxes → keypad button locations

Overlays always on top

Mouse clicks pass through overlays

Terminal logs detected expressions and actions

2️⃣ macOS Setup (Limited Support)

Install Python

brew install python
python3 --version

Install dependencies

pip3 install easyocr pillow pyautogui numpy sympy opencv-python

Grant permissions
Go to System Settings → Privacy & Security

Enable Screen Recording for Terminal/IDE

Enable Accessibility for Terminal/IDE

Restart Terminal after enabling

⚠️ Limitations on macOS

Transparent overlays not supported

ctypes.windll is Windows-only

Auto-clicking depends on accessibility permissions

OCR, solving, and logic still work

macOS users may comment out setup_overlay_boxes() for stability

Configuration
OCR Capture Area
QUESTION_AREA = (410, 182, 711, 227) # (x1, y1, x2, y2)

Adjust this to match where questions appear on your screen.

Keypad Coordinates
KEY_COORDS = {
'0': (486, 613),
'1': (464, 537),
'2': (533, 534), # ...
'OK': (689, 576)
}

Must match screen resolution, application layout, and display scaling (Windows DPI)

How It Works (Pipeline)

Capture OCR region

Convert image to grayscale

Apply thresholding

Detect text with OCR

Normalise operators (×, ÷, etc.)

Fix missing operators

Solve expression

Click digits + OK button

Troubleshooting

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

Notes

Screen coordinates are environment-specific

Intended for educational and experimental use

Logic and overlays are modular and extensible

Quick Start – Imports Reference

All main imports are at the top for easy reference:

import easyocr
from PIL import ImageGrab, Image, ImageTk
import pyautogui
import numpy as np
import tkinter as tk
from sympy import symbols, Eq, solve, sympify, N
import re
import time
import sys
import ctypes
from pynput import keyboard

### Demo of Sparx Solver in action

![Sparx Solver Demo](demo.gif)

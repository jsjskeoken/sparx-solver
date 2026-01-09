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

# ----------------- WINDOWS CONSTANTS -----------------
WS_EX_TRANSPARENT = 0x00000020
WS_EX_LAYERED = 0x00080000
GWL_EXSTYLE = -20

# ----------------- CONFIG -----------------
# Shifting the box right (350 -> 300) and down (100 -> 220) 
# and making it wider/taller to ensure the question fits.
QUESTION_AREA = (410, 182, 711, 227)




KEY_COORDS = {
    '0': (486, 613), '1': (464, 537), '2': (533, 534), '3': (606, 530),
    '4': (453, 456), '5': (531, 460), '6': (615, 455),
    '7': (453, 378), '8': (530, 381), '9': (613, 381), 'OK': (689, 576)
}

POLLING_INTERVAL_MS =1
KEY_PRESS_DELAY = 0
POST_ANSWER_DELAY = 0

# ----------------- MATH SOLVER CLASS -----------------
class MathSolverBot:

    def __init__(self, q_area, key_coords):
        self.question_area = q_area
        self.key_coords = key_coords
        self.reader = easyocr.Reader(['en'])
        self.last_question = ""

        self.setup_gui()
        self.setup_overlay_boxes()

    def setup_gui(self):
        self.root = tk.Tk()
        self.root.title("Question Preview")
        self.root.geometry("300x150+50+50")
        self.root.resizable(False, False)
        self.root.attributes("-topmost", True)

        self.canvas = tk.Canvas(self.root, width=300, height=150)
        self.canvas.pack()
        self.img_tk = None

    def setup_overlay_boxes(self):
        self.overlay_windows = []

        # OCR area - LABEL REMOVED HERE
        x1, y1, x2, y2 = self.question_area
        self.create_overlay_box(
            x1, y1, x2 - x1, y2 - y1,
            "red", ""  # Empty string means no text label
        )

        # Key buttons
        for key, (x, y) in self.key_coords.items():
            self.create_overlay_box(
                x - 25, y - 25, 50, 50,
                "cyan", key
            )

    def create_overlay_box(self, x, y, w, h, color, label):
        win = tk.Toplevel(self.root)
        win.overrideredirect(True)
        win.attributes("-topmost", True)
        win.geometry(f"{w}x{h}+{x}+{y}")

        transparent_bg = "black" 
        win.config(bg=transparent_bg)
        win.attributes("-transparentcolor", transparent_bg)

        canvas = tk.Canvas(win, width=w, height=h, bg=transparent_bg, highlightthickness=0)
        canvas.pack()
        
        canvas.create_rectangle(
            2, 2, w - 2, h - 2,
            outline=color,
            width=3
        )
        
        # Only draw text if a label is provided
        if label:
            canvas.create_text(
                w // 2, 10, 
                text=label,
                fill=color,
                font=("Arial", 10, "bold"),
                anchor="n"
            )

        hwnd = ctypes.windll.user32.GetParent(win.winfo_id())
        styles = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
        new_style = styles | WS_EX_LAYERED | WS_EX_TRANSPARENT
        ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, new_style)

        self.overlay_windows.append(win)

    def normalize_operators(self, expr):
        expr = expr.replace('×', '*').replace('x', '*').replace('X', '*')
        expr = expr.replace('÷', '/').replace(':', '/')
        expr = re.sub(r'[^\d\s\+\-\*/\(\)=?]', '', expr)
        return expr

    def fix_missing_operator(self, expr):
        if '(' not in expr and ')' not in expr and '+' in expr:
            return expr.replace('+', '/', 1)
        div_pattern = r"(\d{3})\s+(\d{1,2})\s*=\s*\?"
        match = re.search(div_pattern, expr)
        if match:
            return f"{match.group(1)} / {match.group(2)} = ?"
        return re.sub(r"(\d+)\s+(\d+)", r"\1 * \2", expr, count=1)

    def finalize_expression(self, expr):
        expr = re.sub(r'\s*([\+\-\*/\(\)=])\s*', r'\1', expr)
        if expr.count('(') > expr.count(')'):
            expr += ')' * (expr.count('(') - expr.count(')'))
        return expr

    def solve_algebra(self, expr):
        try:
            if '?' not in expr:
                result = N(sympify(expr))
                return int(result) if result.is_integer else float(result)
            x = symbols('x')
            lhs, rhs = expr.replace('?', 'x').split('=')
            sol = solve(Eq(sympify(lhs), sympify(rhs)), x)
            if sol:
                result = N(sol[0])
                return int(result) if result.is_integer else float(result)
        except Exception as e:
            print(f"Solver Error: {e}", file=sys.stderr)
        return None

    def click_answer(self, answer):
        print(f"Clicking answer: {answer}")
        for d in str(int(answer)):
            if d in self.key_coords:
                pyautogui.click(self.key_coords[d])
                time.sleep(KEY_PRESS_DELAY)
        pyautogui.click(self.key_coords['OK'])
        time.sleep(POST_ANSWER_DELAY)

    def main_loop(self):
        try:
            img = ImageGrab.grab(bbox=self.question_area)
            img = img.convert("L")
            img = img.point(lambda x: 0 if x < 140 else 255)


           # --- REMOVE PREVIEW ---
# preview = ImageTk.PhotoImage(img.resize((300, 150)))
# self.canvas.create_image(0, 0, anchor=tk.NW, image=preview)
# self.img_tk = preview
# ----------------------

            result = self.reader.readtext(
                np.array(img),
                allowlist='0123456789+-*/()=?xX×÷: ',
                low_text=0.4,
                batch_size=4,
                min_size=5
            )

            question = " ".join(t for _, t, _ in result).strip()
            
            if question and question != self.last_question:
                self.last_question = question
                print(f"Detected: {question}")
                expr = self.finalize_expression(
                    self.fix_missing_operator(
                        self.normalize_operators(question)
                    )
                )
                answer = self.solve_algebra(expr)
                if answer is not None and float(answer).is_integer():
                    self.click_answer(int(answer))
        except Exception as e:
            print(f"Loop Error: {e}")
        self.root.after(POLLING_INTERVAL_MS, self.main_loop)

    def run(self):
        print("MathSolverBot running. Press Ctrl+C in terminal to stop.")
        self.root.after(200, self.main_loop)
        self.root.mainloop()

if __name__ == "__main__":
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass
    MathSolverBot(QUESTION_AREA, KEY_COORDS).run()

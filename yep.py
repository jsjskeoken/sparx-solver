import easyocr
from PIL import ImageGrab, Image
import pyautogui
import numpy as np
import tkinter as tk
from sympy import symbols, Eq, solve, sympify, N
import re
import time
import sys
import ctypes
from pynput import keyboard

# ----------------- DPI & SCALING SETUP -----------------
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass

REF_W = 1366
REF_H = 768
CURR_W, CURR_H = pyautogui.size()
SCALE_X = CURR_W / REF_W
SCALE_Y = CURR_H / REF_H

print(f"Screen: {CURR_W}x{CURR_H} (Scaling: {SCALE_X:.2f}x, {SCALE_Y:.2f}x)")

def s_xy(x, y):
    return (int(x * SCALE_X), int(y * SCALE_Y))

def s_bbox(bbox):
    return (int(bbox[0] * SCALE_X), int(bbox[1] * SCALE_Y), 
            int(bbox[2] * SCALE_X), int(bbox[3] * SCALE_Y))

# ----------------- WINDOWS CONSTANTS -----------------
WS_EX_TRANSPARENT = 0x00000020
WS_EX_LAYERED = 0x00080000
GWL_EXSTYLE = -20

# ----------------- CONFIG (AUTO-SCALED) -----------------
ORIGINAL_QUESTION_AREA = (411, 182, 722, 231)
ORIGINAL_KEY_COORDS = {
    '0': (486, 613), '1': (464, 537), '2': (533, 534), '3': (606, 530),
    '4': (453, 456), '5': (531, 460), '6': (615, 455),
    '7': (453, 378), '8': (530, 381), '9': (613, 381), 'OK': (689, 576)
}

# Automation click areas
ORIGINAL_AUTO_AREA_1 = (510, 686)  # First click after 10 answers
ORIGINAL_AUTO_AREA_2 = (157, 745)  # Second click in sequence
ORIGINAL_AUTO_AREA_3 = (274, 430)  # Third click in sequence

QUESTION_AREA = s_bbox(ORIGINAL_QUESTION_AREA)
KEY_COORDS = {k: s_xy(v[0], v[1]) for k, v in ORIGINAL_KEY_COORDS.items()}
AUTO_AREA_1 = s_xy(ORIGINAL_AUTO_AREA_1[0], ORIGINAL_AUTO_AREA_1[1])
AUTO_AREA_2 = s_xy(ORIGINAL_AUTO_AREA_2[0], ORIGINAL_AUTO_AREA_2[1])
AUTO_AREA_3 = s_xy(ORIGINAL_AUTO_AREA_3[0], ORIGINAL_AUTO_AREA_3[1])

# Mode-specific polling intervals
CLUB_MODE_POLLING = 10
GAMES_MODE_POLLING = 150

KEY_PRESS_DELAY = 0
POST_ANSWER_DELAY = 0

# ----------------- MATH SOLVER CLASS -----------------
class MathSolverBot:

    def __init__(self, q_area, key_coords):
        self.question_area = q_area
        self.key_coords = key_coords
        self.reader = easyocr.Reader(['en'], gpu=True)
        self.last_question = ""
        self.paused = False
        self.overlays_visible = True
        self.club_mode = True
        self.current_polling = CLUB_MODE_POLLING
        
        # Automation counters
        self.answers_count = 0
        self.ready_count = 0
        
        # Pre-compile regex patterns for speed
        self.operator_clean = re.compile(r'[^\d\s\+\-\*/\(\)=?]')
        self.space_clean = re.compile(r'\s*([\+\-\*/\(\)=])\s*')
        self.div_pattern = re.compile(r"(\d{3})\s+(\d{1,2})\s*=\s*\?")
        self.mult_pattern = re.compile(r"(\d+)\s+(\d+)")
        
        # Cache for sympy symbol
        self.x_symbol = symbols('x')

        self.setup_gui()
        self.setup_overlay_boxes()
        self.setup_keyboard_listener()

    def setup_gui(self):
        self.root = tk.Tk()
        self.root.title("Math Solver Bot")
        self.root.geometry("220x180+50+50")
        self.root.resizable(False, False)
        self.root.attributes("-topmost", True)

        status_label = tk.Label(self.root, text="Status:", font=("Arial", 10, "bold"))
        status_label.pack(pady=5)
        
        self.status_text = tk.Label(self.root, text="RUNNING", fg="green", font=("Arial", 12, "bold"))
        self.status_text.pack(pady=2)
        
        self.mode_text = tk.Label(self.root, text="Mode: CLUB (10ms)", fg="blue", font=("Arial", 9, "bold"))
        self.mode_text.pack(pady=2)
        
        # Automation counter display
        self.counter_text = tk.Label(self.root, text="Answers: 0/10 | Ready: 0", fg="orange", font=("Arial", 9, "bold"))
        self.counter_text.pack(pady=2)
        
        info_label = tk.Label(self.root, text="F9: Pause/Resume", font=("Arial", 8))
        info_label.pack(pady=1)
        
        overlay_label = tk.Label(self.root, text="F10: Toggle Overlays", font=("Arial", 8))
        overlay_label.pack(pady=1)
        
        mode_label = tk.Label(self.root, text="F11: Switch Mode", font=("Arial", 8))
        mode_label.pack(pady=1)

    def setup_keyboard_listener(self):
        def on_press(key):
            try:
                if key == keyboard.Key.f9:
                    self.paused = not self.paused
                    status = "PAUSED" if self.paused else "RUNNING"
                    color = "red" if self.paused else "green"
                    self.status_text.config(text=status, fg=color)
                    print(f"Bot {status}")
                elif key == keyboard.Key.f10:
                    self.overlays_visible = not self.overlays_visible
                    self.toggle_overlays()
                    print(f"Overlays {'SHOWN' if self.overlays_visible else 'HIDDEN'}")
                elif key == keyboard.Key.f11:
                    self.club_mode = not self.club_mode
                    self.current_polling = CLUB_MODE_POLLING if self.club_mode else GAMES_MODE_POLLING
                    mode_name = "CLUB (10ms)" if self.club_mode else "GAMES (150ms)"
                    self.mode_text.config(text=f"Mode: {mode_name}")
                    print(f"Switched to {mode_name} mode")
            except Exception as e:
                pass
        
        self.listener = keyboard.Listener(on_press=on_press)
        self.listener.start()

    def setup_overlay_boxes(self):
        self.overlay_windows = []

        x1, y1, x2, y2 = self.question_area
        self.create_overlay_box(
            x1, y1, x2 - x1, y2 - y1,
            "red", ""
        )

        box_size = int(50 * SCALE_X)
        for key, (x, y) in self.key_coords.items():
            self.create_overlay_box(
                x - (box_size // 2), y - (box_size // 2), box_size, box_size,
                "cyan", key
            )
        
        # Automation area highlights
        auto_box_size = int(60 * SCALE_X)
        self.create_overlay_box(
            AUTO_AREA_1[0] - (auto_box_size // 2), AUTO_AREA_1[1] - (auto_box_size // 2),
            auto_box_size, auto_box_size,
            "yellow", "AUTO 1"
        )
        self.create_overlay_box(
            AUTO_AREA_2[0] - (auto_box_size // 2), AUTO_AREA_2[1] - (auto_box_size // 2),
            auto_box_size, auto_box_size,
            "magenta", "AUTO 2"
        )
        self.create_overlay_box(
            AUTO_AREA_3[0] - (auto_box_size // 2), AUTO_AREA_3[1] - (auto_box_size // 2),
            auto_box_size, auto_box_size,
            "lime", "AUTO 3"
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

    def toggle_overlays(self):
        for win in self.overlay_windows:
            if self.overlays_visible:
                win.deiconify()
            else:
                win.withdraw()

    def normalize_operators(self, expr):
        expr = expr.replace('×', '*').replace('x', '*').replace('X', '*').replace('÷', '/').replace(':', '/')
        return self.operator_clean.sub('', expr)

    def fix_missing_operator(self, expr):
        if '(' not in expr and ')' not in expr and '+' in expr:
            return expr.replace('+', '/', 1)
        match = self.div_pattern.search(expr)
        if match:
            return f"{match.group(1)} / {match.group(2)} = ?"
        return self.mult_pattern.sub(r"\1 * \2", expr, count=1)

    def finalize_expression(self, expr):
        expr = self.space_clean.sub(r'\1', expr)
        paren_diff = expr.count('(') - expr.count(')')
        if paren_diff > 0:
            expr += ')' * paren_diff
        return expr

    def solve_algebra(self, expr):
        try:
            if '?' not in expr:
                result = N(sympify(expr))
                return int(result) if result.is_integer else float(result)
            lhs, rhs = expr.replace('?', 'x').split('=')
            sol = solve(Eq(sympify(lhs), sympify(rhs)), self.x_symbol)
            if sol:
                result = N(sol[0])
                return int(result) if result.is_integer else float(result)
        except Exception as e:
            print(f"Solver Error: {e}", file=sys.stderr)
        return None

    def click_answer(self, answer):
        answer_str = str(int(answer))
        print(f"Clicking answer: {answer_str}")
        for d in answer_str:
            pyautogui.click(self.key_coords[d])
            if KEY_PRESS_DELAY > 0:
                time.sleep(KEY_PRESS_DELAY)
        pyautogui.click(self.key_coords['OK'])
        if POST_ANSWER_DELAY > 0:
            time.sleep(POST_ANSWER_DELAY)
        
        # Increment answer counter
        self.answers_count += 1
        self.update_counter_display()
        
        # Check if we hit 10 answers
        if self.answers_count >= 10:
            self.answers_count = 0  # Reset counter
            self.ready_count += 1   # Increment ready
            print(f"[AUTO] 10 answers reached! Ready count: {self.ready_count}")
            
            # Wait 1 second before clicking AUTO_AREA_1
            self.root.after(1000, self.auto_click_area_1_initial)
            
            # Check if ready count is 3
            if self.ready_count >= 3:
                print("[AUTO] Ready count is 3! Starting timed sequence...")
                self.ready_count = 0  # Reset ready count
                self.update_counter_display()
                
                # Wait 10 seconds after AUTO_AREA_1 clicked, then click AUTO_AREA_2
                self.root.after(10000, self.auto_click_area_2)
    
    def auto_click_area_1_initial(self):
        """Click AUTO_AREA_1 after 1 second delay"""
        print(f"[AUTO] Clicking AUTO AREA 1 at {AUTO_AREA_1}")
        pyautogui.click(AUTO_AREA_1)
    
    def auto_click_area_2(self):
        """Click AUTO_AREA_2 after 10 second delay"""
        print(f"[AUTO] Clicking AUTO AREA 2 at {AUTO_AREA_2}")
        pyautogui.click(AUTO_AREA_2)
        
        # Wait 2 seconds, then click AUTO_AREA_3
        self.root.after(2000, self.auto_click_area_3)
    
    def auto_click_area_3(self):
        """Click AUTO_AREA_3 after 2 second delay"""
        print(f"[AUTO] Clicking AUTO AREA 3 at {AUTO_AREA_3}")
        pyautogui.click(AUTO_AREA_3)
        
        # Wait 8 seconds, then click AUTO_AREA_1 (final)
        self.root.after(8000, self.auto_click_area_1_final)
    
    def auto_click_area_1_final(self):
        """Click AUTO_AREA_1 after 2 second delay"""
        print(f"[AUTO] Clicking AUTO AREA 1 (final) at {AUTO_AREA_1}")
        pyautogui.click(AUTO_AREA_1)
    
    def update_counter_display(self):
        """Update the counter text in GUI"""
        self.counter_text.config(text=f"Answers: {self.answers_count}/10 | Ready: {self.ready_count}")

    def main_loop(self):
        try:
            if not self.paused:
                img = ImageGrab.grab(bbox=self.question_area)
                
                # Fast image preprocessing
                img_array = np.array(img.convert("L"))
                img_array[img_array < 140] = 0
                img_array[img_array >= 140] = 255

                result = self.reader.readtext(
                    img_array,
                    allowlist='0123456789+-*/()=?xX×÷: ',
                    low_text=0.4,
                    batch_size=4,
                    min_size=5
                )

                if result:
                    question = " ".join(t for _, t, _ in result)
                    
                    if question != self.last_question:
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
        
        # Use current polling interval based on mode
        self.root.after(self.current_polling, self.main_loop)

    def run(self):
        print("MathSolverBot running.")
        print("F9: Pause/Resume | F10: Toggle Overlays | F11: Switch Mode | Ctrl+C: Stop")
        print("Starting in CLUB mode (10ms polling)")
        self.root.after(200, self.main_loop)
        self.root.mainloop()

if __name__ == "__main__":
    MathSolverBot(QUESTION_AREA, KEY_COORDS).run()

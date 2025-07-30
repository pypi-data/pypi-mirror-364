# side_panel_app.py

import tkinter as tk
from tkinter import ttk, messagebox
import os
import subprocess
import sys
from datetime import datetime, timedelta

NOTEPAD_FILE = "sidepanel_notepad.txt"
TODO_FILE = "sidepanel_todo.txt"
TIMER_FILE = "sidepanel_timer.txt"

def get_screen_geometry():
    root = tk.Tk()
    root.withdraw()
    width = root.winfo_screenwidth()
    height = root.winfo_screenheight()
    root.destroy()
    return width, height

def is_mac():
    return sys.platform == "darwin"

def add_reminder_applescript(task):
    script = f'''
    tell application "Reminders"
        set newReminder to make new reminder with properties {{name:"{task}"}}
    end tell
    '''
    try:
        subprocess.run(["osascript", "-e", script], check=True)
    except Exception as e:
        print(f"Error adding reminder: {e}")

def complete_reminder_applescript(task):
    script = f'''
    tell application "Reminders"
        set theReminders to reminders whose name is "{task}" and completed is false
        repeat with r in theReminders
            set completed of r to true
        end repeat
    end tell
    '''
    try:
        subprocess.run(["osascript", "-e", script], check=True)
    except Exception as e:
        print(f"Error completing reminder: {e}")

def delete_reminder_applescript(task):
    script = f'''
    tell application "Reminders"
        set theReminders to reminders whose name is "{task}" and completed is false
        repeat with r in theReminders
            delete r
        end repeat
    end tell
    '''
    try:
        subprocess.run(["osascript", "-e", script], check=True)
    except Exception as e:
        print(f"Error deleting reminder: {e}")

def parse_date(date_str):
    # Try several formats
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%B %d, %Y", "%d %B %Y", "%b %d, %Y", "%d %b %Y"):
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    # Try parsing as ISO format
    try:
        return datetime.fromisoformat(date_str)
    except Exception:
        pass
    return None

class SidePanelApp:
    def __init__(self):
        self.screen_width, self.screen_height = get_screen_geometry()
        self.button_width = 40
        self.button_height = 120
        self.panel_open = False

        # Main root for the button
        self.root = tk.Tk()
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.attributes("-alpha", 0.5)  # Semi-transparent
        self.root.geometry(f"{self.button_width}x{self.button_height}+{self.screen_width - self.button_width}+{(self.screen_height - self.button_height)//2}")
        self.root.config(bg="systemTransparent")  # For macOS, makes background transparent
        self.root.lift()
        self.root.focus_force()

        self.button = tk.Canvas(self.root, width=self.button_width, height=self.button_height, bg="systemTransparent", highlightthickness=0)
        self.button.pack(fill="both", expand=True)
        self.button.create_rectangle(5, 5, self.button_width-5, self.button_height-5, fill="gray60", outline="white", width=2, tags="rect")
        self.button.bind("<Button-1>", self.animate_and_open_panel)

        self.panel = None

        # Start the timer update loop
        self.root.after(1000, self.update_timer)

    def animate_and_open_panel(self, event):
        # Animate: flash color
        self.button.itemconfig("rect", fill="gray80")
        self.root.update()
        self.root.after(100)
        self.button.itemconfig("rect", fill="gray60")
        self.root.update()
        self.open_panel()

    def open_panel(self):
        if self.panel is not None:
            return  # Already open

        self.panel_open = True

        panel_width = self.screen_width // 3
        panel_height = self.screen_height - 100  # Subtract 100 from height
        panel_x = self.screen_width - panel_width
        panel_y = 0

        self.panel = tk.Toplevel(self.root)
        # self.panel.overrideredirect(True)  # Removed for keyboard input
        self.panel.attributes("-topmost", True)
        self.panel.geometry(f"{panel_width}x{panel_height}+{panel_x}+{panel_y}")
        self.panel.config(bg="white")
        self.panel.lift()
        self.panel.focus_force()

        # Tabbed interface
        notebook = ttk.Notebook(self.panel)
        notebook.pack(fill="both", expand=True)

        # Notepad tab
        notepad_frame = tk.Frame(notebook, bg="white")
        self.text_area = tk.Text(notepad_frame, wrap="word", font=("Consolas", 12))
        self.text_area.pack(fill="both", expand=True, padx=10, pady=10)
        self.text_area.bind("<<Modified>>", self.save_notepad)
        self.load_notepad()
        notebook.add(notepad_frame, text="Notepad")

        # To-Do tab
        todo_frame = tk.Frame(notebook, bg="white")
        self.todo_items = []
        self.todo_vars = []
        self.todo_frame_inner = tk.Frame(todo_frame, bg="white")
        self.todo_frame_inner.pack(fill="both", expand=True, padx=10, pady=10)
        self.load_todo_items()

        add_frame = tk.Frame(todo_frame, bg="white")
        add_frame.pack(fill="x", padx=10, pady=(0,10))
        self.new_task_var = tk.StringVar()
        new_task_entry = tk.Entry(add_frame, textvariable=self.new_task_var, font=("Arial", 12))
        new_task_entry.pack(side="left", fill="x", expand=True)
        new_task_entry.bind("<Return>", lambda e: self.add_todo_item())
        tk.Button(add_frame, text="Add", command=self.add_todo_item).pack(side="left", padx=5)
        tk.Button(add_frame, text="Open Reminders", command=self.open_apple_reminders).pack(side="left", padx=5)
        notebook.add(todo_frame, text="To-Do")

        # Countdown Timer tab
        timer_frame = tk.Frame(notebook, bg="white")
        self.timer_target_var = tk.StringVar()
        self.timer_label = tk.Label(timer_frame, text="", font=("Consolas", 36, "bold"), bg="white", fg="black")
        self.timer_label.pack(pady=40, padx=10, fill="x")
        timer_entry_frame = tk.Frame(timer_frame, bg="white")
        timer_entry_frame.pack(pady=10)
        tk.Label(timer_entry_frame, text="Target date (e.g. 2024-08-31):", font=("Arial", 12), bg="white").pack(side="left")
        timer_entry = tk.Entry(timer_entry_frame, textvariable=self.timer_target_var, font=("Arial", 12), width=20)
        timer_entry.pack(side="left", padx=5)
        tk.Button(timer_entry_frame, text="Set", command=self.set_timer_target).pack(side="left", padx=5)
        self.timer_status = tk.Label(timer_frame, text="", font=("Arial", 10), bg="white", fg="red")
        self.timer_status.pack(pady=5)
        self.load_timer_target()
        notebook.add(timer_frame, text="Countdown")

        # Close button
        close_btn = tk.Button(self.panel, text="Close", command=self.close_panel)
        close_btn.pack(pady=10)

        # Optionally hide the button window
        self.root.withdraw()

    def load_notepad(self):
        if os.path.exists(NOTEPAD_FILE):
            with open(NOTEPAD_FILE, "r", encoding="utf-8") as f:
                content = f.read()
            self.text_area.insert("1.0", content)
        self.text_area.edit_modified(False)

    def save_notepad(self, event=None):
        if self.text_area.edit_modified():
            content = self.text_area.get("1.0", tk.END)
            with open(NOTEPAD_FILE, "w", encoding="utf-8") as f:
                f.write(content.rstrip())
            self.text_area.edit_modified(False)

    # --- To-Do List Methods ---

    def load_todo_items(self):
        self.todo_items.clear()
        self.todo_vars.clear()
        for widget in self.todo_frame_inner.winfo_children():
            widget.destroy()
        if os.path.exists(TODO_FILE):
            with open(TODO_FILE, "r", encoding="utf-8") as f:
                lines = f.readlines()
            for line in lines:
                line = line.rstrip("\n")
                if line.startswith("[x] "):
                    self.add_todo_item(line[4:], checked=True, save=False)
                elif line.startswith("[ ] "):
                    self.add_todo_item(line[4:], checked=False, save=False)
        self.save_todo_items()

    def save_todo_items(self):
        with open(TODO_FILE, "w", encoding="utf-8") as f:
            for var, text in zip(self.todo_vars, self.todo_items):
                prefix = "[x] " if var.get() else "[ ] "
                f.write(prefix + text + "\n")

    def add_todo_item(self, text=None, checked=False, save=True):
        if text is None:
            text = self.new_task_var.get().strip()
            if not text:
                return
            self.new_task_var.set("")
            # Add to Apple Reminders if on macOS
            if is_mac():
                add_reminder_applescript(text)
        var = tk.BooleanVar(value=checked)
        cb = tk.Checkbutton(self.todo_frame_inner, text="• " + text, variable=var, font=("Arial", 12), bg="white", anchor="w", command=lambda: self.toggle_todo_item(var, text))
        cb.pack(fill="x", anchor="w", pady=2)
        btn = tk.Button(self.todo_frame_inner, text="Remove", font=("Arial", 10), command=lambda: self.remove_todo_item(cb, btn, var, text))
        btn.pack(anchor="e", pady=2)
        self.todo_items.append(text)
        self.todo_vars.append(var)
        if save:
            self.save_todo_items()

    def toggle_todo_item(self, var, text):
        # If checked, mark as done in Reminders
        if var.get() and is_mac():
            complete_reminder_applescript(text)
        self.save_todo_items()

    def remove_todo_item(self, cb, btn, var, text):
        idx = None
        for i, (v, t) in enumerate(zip(self.todo_vars, self.todo_items)):
            if v == var and t == text:
                idx = i
                break
        if idx is not None:
            self.todo_items.pop(idx)
            self.todo_vars.pop(idx)
        cb.destroy()
        btn.destroy()
        # Remove from Apple Reminders if on macOS
        if is_mac():
            delete_reminder_applescript(text)
        self.save_todo_items()

    def open_apple_reminders(self):
        if is_mac():
            try:
                subprocess.Popen(["open", "-a", "Reminders"])
            except Exception as e:
                messagebox.showerror("Error", f"Could not open Reminders: {e}")
        else:
            messagebox.showinfo("Not Supported", "Apple Reminders integration is only available on macOS.")

    # --- End To-Do List Methods ---

    # --- Countdown Timer Methods ---

    def load_timer_target(self):
        self.timer_target = None
        if os.path.exists(TIMER_FILE):
            with open(TIMER_FILE, "r", encoding="utf-8") as f:
                date_str = f.read().strip()
                self.timer_target_var.set(date_str)
                self.timer_target = parse_date(date_str)

    def save_timer_target(self):
        with open(TIMER_FILE, "w", encoding="utf-8") as f:
            f.write(self.timer_target_var.get().strip())

    def set_timer_target(self):
        date_str = self.timer_target_var.get().strip()
        dt = parse_date(date_str)
        if not dt:
            self.timer_status.config(text="Invalid date format. Try YYYY-MM-DD or 31/08/2025.")
            return
        self.timer_target = dt
        self.save_timer_target()
        self.timer_status.config(text="")

    def update_timer(self):
        # Only update if panel is open and timer_label exists
        if getattr(self, "panel_open", False) and hasattr(self, "timer_label") and self.timer_label.winfo_exists():
            now = datetime.now()
            target = getattr(self, "timer_target", None)
            if not target:
                date_str = self.timer_target_var.get().strip()
                target = parse_date(date_str)
                if target:
                    self.timer_target = target
            if target:
                delta = target - now
                if delta.total_seconds() > 0:
                    days = delta.days
                    hours, rem = divmod(delta.seconds, 3600)
                    minutes, seconds = divmod(rem, 60)
                    self.timer_label.config(
                        text=f"{days}d {hours:02}h {minutes:02}m {seconds:02}s"
                    )
                else:
                    self.timer_label.config(text="Time's up!")
            else:
                self.timer_label.config(text="Set a target date.")
        self.root.after(1000, self.update_timer)

    # --- End Countdown Timer Methods ---

    def close_panel(self):
        if self.panel is not None:
            self.panel.destroy()
            self.panel = None
            self.panel_open = False
            self.root.deiconify()
            self.root.lift()
            self.root.focus_force()

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    SidePanelApp().run()

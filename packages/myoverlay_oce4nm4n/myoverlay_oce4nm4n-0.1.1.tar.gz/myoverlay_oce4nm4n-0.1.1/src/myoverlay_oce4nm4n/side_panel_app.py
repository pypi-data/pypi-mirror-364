import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import os
import subprocess
import sys
from datetime import datetime, timedelta
import appdirs

APP_NAME = "myoverlay"
APP_AUTHOR = "oce4nm4n"

# Use appdirs to get a user-specific, OS-appropriate data directory
DATA_DIR = appdirs.user_data_dir(APP_NAME, APP_AUTHOR)
os.makedirs(DATA_DIR, exist_ok=True)

NOTEPAD_DIR = os.path.join(DATA_DIR, "sidepanel_notepads")
os.makedirs(NOTEPAD_DIR, exist_ok=True)

TODO_FILE = os.path.join(DATA_DIR, "sidepanel_todo.txt")
TIMERS_FILE = os.path.join(DATA_DIR, "sidepanel_timers.txt")

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
        self.setup_notepad_tab(notepad_frame)
        notebook.add(notepad_frame, text="Notepads")

        # To-Do tab
        todo_frame = tk.Frame(notebook, bg="white")
        self.setup_todo_tab(todo_frame)
        notebook.add(todo_frame, text="To-Do")

        # Countdown Timer tab
        timer_frame = tk.Frame(notebook, bg="white")
        self.setup_timer_tab(timer_frame)
        notebook.add(timer_frame, text="Countdowns")

        # Close button
        close_btn = tk.Button(self.panel, text="Close", command=self.close_panel)
        close_btn.pack(pady=10)

        # Optionally hide the button window
        self.root.withdraw()

    # --- Multiple Notepads ---

    def setup_notepad_tab(self, frame):
        top = tk.Frame(frame, bg="white")
        top.pack(fill="x", padx=10, pady=(10, 0))

        self.notepad_names = self.get_notepad_names()
        self.current_notepad = tk.StringVar()
        if self.notepad_names:
            self.current_notepad.set(self.notepad_names[0])
        else:
            self.current_notepad.set("Default")
            self.notepad_names = ["Default"]
            self.save_notepad("Default", "")

        self.notepad_menu = ttk.Combobox(top, values=self.notepad_names, textvariable=self.current_notepad, state="readonly", width=20)
        self.notepad_menu.pack(side="left")
        self.notepad_menu.bind("<<ComboboxSelected>>", self.load_selected_notepad)

        tk.Button(top, text="New", command=self.create_new_notepad).pack(side="left", padx=5)
        tk.Button(top, text="Delete", command=self.delete_current_notepad).pack(side="left", padx=5)

        self.text_area = tk.Text(frame, wrap="word", font=("Consolas", 12))
        self.text_area.pack(fill="both", expand=True, padx=10, pady=10)
        self.text_area.bind("<<Modified>>", self.save_current_notepad)
        self.load_selected_notepad()

    def get_notepad_names(self):
        files = os.listdir(NOTEPAD_DIR)
        names = [f[:-4] for f in files if f.endswith(".txt")]
        return sorted(names) if names else []

    def notepad_file(self, name):
        safe = "".join(c for c in name if c.isalnum() or c in (' ', '_', '-')).rstrip()
        return os.path.join(NOTEPAD_DIR, f"{safe}.txt")

    def load_selected_notepad(self, event=None):
        name = self.current_notepad.get()
        file = self.notepad_file(name)
        self.text_area.delete("1.0", tk.END)
        if os.path.exists(file):
            with open(file, "r", encoding="utf-8") as f:
                self.text_area.insert("1.0", f.read())
        self.text_area.edit_modified(False)

    def save_current_notepad(self, event=None):
        if self.text_area.edit_modified():
            name = self.current_notepad.get()
            content = self.text_area.get("1.0", tk.END)
            self.save_notepad(name, content)
            self.text_area.edit_modified(False)

    def save_notepad(self, name, content):
        file = self.notepad_file(name)
        with open(file, "w", encoding="utf-8") as f:
            f.write(content.rstrip())

    def create_new_notepad(self):
        name = simpledialog.askstring("New Notepad", "Enter notepad name:", parent=self.panel)
        if not name:
            return
        name = name.strip()
        if not name or name in self.notepad_names:
            messagebox.showerror("Error", "Invalid or duplicate notepad name.")
            return
        self.notepad_names.append(name)
        self.notepad_menu["values"] = self.notepad_names
        self.current_notepad.set(name)
        self.save_notepad(name, "")
        self.load_selected_notepad()

    def delete_current_notepad(self):
        name = self.current_notepad.get()
        if len(self.notepad_names) == 1:
            messagebox.showerror("Error", "At least one notepad must exist.")
            return
        if messagebox.askyesno("Delete Notepad", f"Delete notepad '{name}'?"):
            file = self.notepad_file(name)
            try:
                os.remove(file)
            except Exception:
                pass
            self.notepad_names.remove(name)
            self.notepad_menu["values"] = self.notepad_names
            self.current_notepad.set(self.notepad_names[0])
            self.load_selected_notepad()

    # --- To-Do List Methods ---

    def setup_todo_tab(self, frame):
        self.todo_items = []
        self.todo_vars = []
        self.todo_frame_inner = tk.Frame(frame, bg="white")
        self.todo_frame_inner.pack(fill="both", expand=True, padx=10, pady=10)
        self.load_todo_items()

        add_frame = tk.Frame(frame, bg="white")
        add_frame.pack(fill="x", padx=10, pady=(0,10))
        self.new_task_var = tk.StringVar()
        new_task_entry = tk.Entry(add_frame, textvariable=self.new_task_var, font=("Arial", 12))
        new_task_entry.pack(side="left", fill="x", expand=True)
        new_task_entry.bind("<Return>", lambda e: self.add_todo_item())
        tk.Button(add_frame, text="Add", command=self.add_todo_item).pack(side="left", padx=5)
        tk.Button(add_frame, text="Open Reminders", command=self.open_apple_reminders).pack(side="left", padx=5)

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

    # --- Multiple Timers ---

    def setup_timer_tab(self, frame):
        self.timers = self.load_timers()
        self.timer_vars = {}
        self.timer_labels = {}
        self.timer_entries = {}
        self.timer_status_labels = {}

        # Make the timers_frame expand horizontally
        self.timers_frame = tk.Frame(frame, bg="white")
        self.timers_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.render_timers()

        add_frame = tk.Frame(frame, bg="white")
        add_frame.pack(fill="x", padx=10, pady=(0,10))
        tk.Button(add_frame, text="Add Timer", command=self.add_timer_dialog).pack(side="left", padx=5)

    def render_timers(self):
        for widget in self.timers_frame.winfo_children():
            widget.destroy()
        self.timer_vars.clear()
        self.timer_labels.clear()
        self.timer_entries.clear()
        self.timer_status_labels.clear()
        for idx, (name, date_str) in enumerate(self.timers.items()):
            self.add_timer_row(name, date_str, idx)

    def add_timer_row(self, name, date_str, idx):
        # Outer frame for each timer
        timer_outer = tk.Frame(self.timers_frame, bg="white")
        timer_outer.pack(fill="x", expand=True, pady=(0, 0))

        # --- Row 1: Name, Countdown, Delete ---
        row1 = tk.Frame(timer_outer, bg="white")
        row1.pack(fill="x", expand=True)

        # Name label
        tk.Label(row1, text=name, font=("Arial", 12, "bold"), bg="white").pack(side="left", padx=5)

        # Countdown label (expands)
        label = tk.Label(row1, text="", font=("Consolas", 18, "bold"), bg="white", fg="black")
        label.pack(side="left", padx=10, fill="x", expand=True)

        # Delete button (right-aligned)
        tk.Button(row1, text="Delete", command=lambda n=name: self.delete_timer(n)).pack(side="right", padx=5)

        # --- Row 2: Date entry, Set, Status ---
        row2 = tk.Frame(timer_outer, bg="white")
        row2.pack(fill="x", expand=True, pady=(0, 5))

        # Date entry with placeholder
        var = tk.StringVar()
        entry = tk.Entry(row2, textvariable=var, font=("Arial", 12), width=15)
        placeholder = "YYYY-MM-DD"
        if not date_str:
            var.set(placeholder)
            entry.config(fg="gray", bg="#f0f0f0")
        else:
            var.set(date_str)
            entry.config(fg="black", bg="white")
        entry.pack(side="left", padx=5)
        entry.bind("<FocusIn>", lambda e, v=var, ent=entry: self._clear_placeholder(v, ent, placeholder))
        entry.bind("<FocusOut>", lambda e, v=var, ent=entry: self._add_placeholder(v, ent, placeholder))

        # Set button
        tk.Button(row2, text="Set", command=lambda n=name, v=var: self.set_timer_target(n, v)).pack(side="left", padx=5)

        # Status label
        status = tk.Label(row2, text="", font=("Arial", 10), bg="white", fg="red")
        status.pack(side="left", padx=5)

        # Separator
        sep = ttk.Separator(self.timers_frame, orient="horizontal")
        sep.pack(fill="x", pady=2)

        self.timer_vars[name] = var
        self.timer_labels[name] = label
        self.timer_entries[name] = entry
        self.timer_status_labels[name] = status


    def _clear_placeholder(self, var, entry, placeholder):
        if var.get() == placeholder:
            var.set("")
            entry.config(fg="black", bg="white")

    def _add_placeholder(self, var, entry, placeholder):
        if not var.get():
            var.set(placeholder)
            entry.config(fg="gray", bg="#f0f0f0")

    def add_timer_dialog(self):
        name = simpledialog.askstring("New Timer", "Enter timer name:", parent=self.panel)
        if not name:
            return
        name = name.strip()
        if not name or name in self.timers:
            messagebox.showerror("Error", "Invalid or duplicate timer name.")
            return
        self.timers[name] = ""
        self.save_timers()
        self.render_timers()

    def delete_timer(self, name):
        if name in self.timers:
            del self.timers[name]
            self.save_timers()
            self.render_timers()

    def set_timer_target(self, name, var):
        date_str = var.get().strip()
        placeholder = "YYYY-MM-DD"
        if date_str == placeholder:
            self.timer_status_labels[name].config(text="Please enter a date.")
            return
        dt = parse_date(date_str)
        if not dt:
            self.timer_status_labels[name].config(text="Invalid date format. Try YYYY-MM-DD or 31/08/2025.")
            return
        self.timers[name] = date_str
        self.save_timers()
        self.timer_status_labels[name].config(text="")

    def update_timer(self):
        # Only update if panel is open and timer_labels exist
        if getattr(self, "panel_open", False) and hasattr(self, "timer_labels"):
            now = datetime.now()
            for name, var in self.timer_vars.items():
                date_str = var.get().strip()
                placeholder = "YYYY-MM-DD"
                if date_str == placeholder:
                    self.timer_labels[name].config(text="Set a date.")
                    continue
                target = parse_date(date_str)
                label = self.timer_labels[name]
                if target:
                    delta = target - now
                    if delta.total_seconds() > 0:
                        days = delta.days
                        hours, rem = divmod(delta.seconds, 3600)
                        minutes, seconds = divmod(rem, 60)
                        label.config(
                            text=f"{days}d {hours:02}h {minutes:02}m {seconds:02}s"
                        )
                    else:
                        label.config(text="Time's up!")
                else:
                    label.config(text="Set a date.")
        self.root.after(1000, self.update_timer)

    def load_timers(self):
        timers = {}
        if os.path.exists(TIMERS_FILE):
            with open(TIMERS_FILE, "r", encoding="utf-8") as f:
                for line in f:
                    if "::" in line:
                        name, date_str = line.rstrip("\n").split("::", 1)
                        timers[name] = date_str
        return timers

    def save_timers(self):
        with open(TIMERS_FILE, "w", encoding="utf-8") as f:
            for name, date_str in self.timers.items():
                f.write(f"{name}::{date_str}\n")

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

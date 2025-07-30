# SidePanelApp

A macOS-friendly Python/Tkinter floating sidebar with:
- **Always-on-top, semi-transparent button** on the right edge of the screen made with the help of AI
- **Notepad** tab (auto-saves to file)
- **To-Do list** tab with Apple Reminders integration (add, complete, and remove tasks)
- **Countdown Timer** tab (counts down to a specified date)

---

## Features

- **Button Overlay:** Small, draggable, semi-transparent button always on top; click to open the sidebar.
- **Notepad:** Write quick notes, auto-saved to `sidepanel_notepad.txt`.
- **To-Do List:** Add, check off, and remove tasks. Tasks are synced with Apple Reminders on macOS.
- **Countdown Timer:** Enter a target date and see a live countdown in days, hours, minutes, and seconds.
- **All data is saved locally and restored between sessions.**

---

## Requirements

- Python 3.7+
- macOS recommended for Reminders integration (other platforms work, but Reminders sync is disabled)
- No external dependencies required

---

## Usage

1. **Clone or copy the script:**
    ```sh
    git clone https://github.com/Oce4nM4n/myOverlay
    cd myOverlay
    ```

2. **Run:**
    ```sh
    python main.py
    ```

3. **How it works:**
    - A small, vertical button appears on the right edge of your screen.
    - Click the button to open the sidebar with tabs for Notepad, To-Do, and Countdown Timer.
    - Data is saved in the current directory:
        - `sidepanel_notepad.txt`
        - `sidepanel_todo.txt`
        - `sidepanel_timer.txt`

---

## Apple Reminders Integration

- **macOS only:**
  - Adding a task in the To-Do tab also adds it to Reminders.
  - Checking a task marks it as completed in Reminders.
  - Removing a task deletes it from Reminders.
- **Other platforms:**
  - The To-Do tab works locally, but Reminders sync don't.

---


## Troubleshooting

- If you cannot type in the sidebar, ensure you are not running the sidebar in "overrideredirect" mode (the provided code disables this for the sidebar panel).
- On macOS, the first time you run the app, you may be prompted for Automation permissions for AppleScript Reminders integration.

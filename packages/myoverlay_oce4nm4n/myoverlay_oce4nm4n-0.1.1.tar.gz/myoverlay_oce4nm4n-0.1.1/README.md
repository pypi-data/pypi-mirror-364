# SidePanelApp

A macOS-friendly Python/Tkinter floating sidebar with:
- **Always-on-top, semi-transparent button** on the right edge of the screen
- **Notepads** tab (auto-saves your notes to files)
- **To-Do list** tab with Apple Reminders integration (add, complete, and remove tasks)
- **Countdown Timers** tab (with separate timers which count down to a specified date)

---

## Features

- **Button Overlay:** Small, draggable, semi-transparent button always on top; click to open the sidebar.
- **Notepad:** Write quick notes, auto-saved to `sidepanel_notepad.txt`.
- **To-Do List:** Add, check off, and remove tasks. Tasks are synced with Apple Reminders on macOS.
- **Countdown Timer:** Enter a target date and see a live countdown in days, hours, minutes, and seconds.
- **All data is saved locally and restored between sessions:** The notes, todos, and timers are stored as plain `.txt` files in a user-specific application data directory:
	- **Windows:** `C:\Users\<YourUsername>\AppData\Local\myoverlay\`
	- **macOS:** `/Users/<YourUsername>/Library/Application Support/myoverlay/`
	- **Linux:** `/home/<yourusername>/.local/share/myoverlay/`

---

## Requirements

- Python 3.7+
- macOS recommended for Reminders integration (other platforms may work, but Reminders sync is disabled)
- No external dependencies required

---

## Run with pypi

1. **Run:**
	```sh
	pip install myoverlay_oce4nm4n
	```

2. **Run:**
	```sh
	myOverlay
	```
	**or**
	```sh
	python -m myoverlay_oce4nm4n
	```

	> **Note for macOS users:**
	> Use `pip3` instead of `pip` and `python3` instead of `python` if needed:
	> ```sh
	> pip3 install myoverlay_oce4nm4n
	> python3 -m myoverlay_oce4nm4n
	> ```

## Download script and run

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
	- The To-Do tab works locally, but Reminders sync doesn't.

---

## Troubleshooting

- If you cannot type in the sidebar, ensure you are not running the sidebar in "overrideredirect" mode (the provided code disables this for the sidebar panel).
- On macOS, the first time you run the app, you may be prompted for Automation permissions for AppleScript Reminders integration.

---

## Disclaimer

- Made with the help of AI


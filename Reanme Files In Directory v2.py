#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RonsTechHub File Organizer Tool (v2 - robust)
- Always shows a main window so you can see the app is running.
- If Pillow (PIL) is missing, the app still works (logo optional).
- On launch, prompts to choose a folder and renames files sequentially.
"""

import os
import sys
import tkinter as tk
from tkinter import filedialog, ttk

APP_TITLE = "RonsTechHub File Organizer Tool"
LOGO_FILENAME = "RTH Logo.png"   # Put this PNG file next to this script

# Try importing Pillow, but do not fail if not installed
PIL_AVAILABLE = True
try:
    from PIL import Image, ImageTk  # type: ignore
except Exception:
    PIL_AVAILABLE = False

def resource_path(relative_path: str) -> str:
    try:
        base_path = sys._MEIPASS  # type: ignore[attr-defined]
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

def center_window(win):
    win.update_idletasks()
    w = win.winfo_width()
    h = win.winfo_height()
    sw = win.winfo_screenwidth()
    sh = win.winfo_screenheight()
    x = int((sw - w) / 2)
    y = int((sh - h) / 2)
    win.geometry(f"{w}x{h}+{x}+{y}")

def try_load_logo(max_height=40):
    path = resource_path(LOGO_FILENAME)
    if not os.path.isfile(path):
        return None
    # Try Pillow first
    if PIL_AVAILABLE:
        try:
            img = Image.open(path).convert("RGBA")
            ratio = max(1, img.height) / max_height
            new_w = max(1, int(img.width / ratio))
            new_h = max(1, int(img.height / ratio))
            img = img.resize((new_w, new_h), Image.LANCZOS)
            return ImageTk.PhotoImage(img)
        except Exception:
            pass
    # Fallback: try tk.PhotoImage (PNG supported on most Tk builds)
    try:
        return tk.PhotoImage(file=path)
    except Exception:
        return None

def set_window_icon(win, logo_photo):
    try:
        if logo_photo is not None:
            win.iconphoto(True, logo_photo)
    except Exception:
        pass

def popup(parent, title, message, logo_photo=None):
    top = tk.Toplevel(parent)
    top.title(title)
    set_window_icon(top, logo_photo)
    top.resizable(False, False)

    container = ttk.Frame(top, padding=12)
    container.pack(fill="both", expand=True)

    header = ttk.Frame(container)
    header.pack(fill="x", pady=(0, 8))

    if logo_photo is not None:
        ttk.Label(header, image=logo_photo).pack(side="left", padx=(0, 8))

    ttk.Label(header, text=title, font=("", 12, "bold")).pack(side="left")
    ttk.Label(container, text=message, wraplength=480, justify="left").pack(fill="x", pady=(6, 12))

    ttk.Button(container, text="OK", command=top.destroy).pack(side="right")
    top.update_idletasks()
    center_window(top)
    top.grab_set()
    parent.wait_window(top)

def confirm(parent, title, message, logo_photo=None):
    result = {"ok": False}
    top = tk.Toplevel(parent)
    top.title(title)
    set_window_icon(top, logo_photo)
    top.resizable(False, False)

    container = ttk.Frame(top, padding=12)
    container.pack(fill="both", expand=True)

    header = ttk.Frame(container)
    header.pack(fill="x", pady=(0, 8))

    if logo_photo is not None:
        ttk.Label(header, image=logo_photo).pack(side="left", padx=(0, 8))

    ttk.Label(header, text=title, font=("", 12, "bold")).pack(side="left")
    ttk.Label(container, text=message, wraplength=480, justify="left").pack(fill="x", pady=(6, 12))

    btns = ttk.Frame(container)
    btns.pack(fill="x", pady=(6,0))
    def ok():
        result["ok"] = True
        top.destroy()
    ttk.Button(btns, text="Cancel", command=top.destroy).pack(side="right", padx=(8,0))
    ttk.Button(btns, text="OK", command=ok).pack(side="right")

    top.update_idletasks()
    center_window(top)
    top.grab_set()
    parent.wait_window(top)
    return result["ok"]

def get_files_sorted(directory_path):
    entries = []
    for name in os.listdir(directory_path):
        full = os.path.join(directory_path, name)
        if os.path.isfile(full):
            entries.append(name)
    entries.sort()
    return entries

def safe_two_phase_rename(directory_path, files):
    temp_names = []
    for i, old_name in enumerate(files, start=1):
        old_path = os.path.join(directory_path, old_name)
        root, ext = os.path.splitext(old_name)
        temp_name = f"__tmp_renamer_{i}{ext}"
        temp_path = os.path.join(directory_path, temp_name)
        counter = 1
        while os.path.exists(temp_path):
            temp_name = f"__tmp_renamer_{i}_{counter}{ext}"
            temp_path = os.path.join(directory_path, temp_name)
            counter += 1
        os.rename(old_path, temp_path)
        temp_names.append(temp_name)

    count = 0
    for i, temp_name in enumerate(temp_names, start=1):
        temp_path = os.path.join(directory_path, temp_name)
        _, ext = os.path.splitext(temp_name)
        new_name = f"part {i}{ext}"
        new_path = os.path.join(directory_path, new_name)
        if os.path.exists(new_path):
            suffix = 1
            while True:
                candidate = os.path.join(directory_path, f"part {i} ({suffix}){ext}")
                if not os.path.exists(candidate):
                    new_path = candidate
                    break
                suffix += 1
        os.rename(temp_path, new_path)
        count += 1
    return count

def rename_files_sequentially(directory_path):
    if not os.path.isdir(directory_path):
        raise FileNotFoundError(f"Directory '{directory_path}' not found.")
    files = get_files_sorted(directory_path)
    if not files:
        return 0
    return safe_two_phase_rename(directory_path, files)

def start_flow(root, logo_photo):
    # Ask for folder
    directory = filedialog.askdirectory(title=f"{APP_TITLE} — Choose a folder")
    if not directory:
        popup(root, APP_TITLE, "No folder selected. Nothing to do.", logo_photo=logo_photo)
        return
    try:
        file_count = len(get_files_sorted(directory))
    except Exception as e:
        popup(root, APP_TITLE, f"Could not read that folder:\n{e}", logo_photo=logo_photo)
        return
    if file_count == 0:
        popup(root, APP_TITLE, "There are no files in that folder to rename.", logo_photo=logo_photo)
        return
    if not confirm(root, APP_TITLE, f"Rename {file_count} files in:\n\n{directory}\n\nProceed?", logo_photo=logo_photo):
        popup(root, APP_TITLE, "Operation cancelled.", logo_photo=logo_photo)
        return
    try:
        renamed = rename_files_sequentially(directory)
        popup(root, APP_TITLE, f"Done! Total files renamed: {renamed}", logo_photo=logo_photo)
    except Exception as e:
        popup(root, APP_TITLE, f"An error occurred:\n{e}", logo_photo=logo_photo)

def main():
    root = tk.Tk()
    root.title(APP_TITLE)
    root.geometry("520x260")
    logo_photo = try_load_logo(max_height=36)
    set_window_icon(root, logo_photo)

    # UI
    container = ttk.Frame(root, padding=16)
    container.pack(fill="both", expand=True)

    header = ttk.Frame(container)
    header.pack(fill="x", pady=(0, 12))
    if logo_photo is not None:
        ttk.Label(header, image=logo_photo).pack(side="left", padx=(0, 8))
    ttk.Label(header, text=APP_TITLE, font=("", 14, "bold")).pack(side="left")

    ttk.Label(container, text="Choose a folder and the tool will rename files as:\npart 1.ext, part 2.ext, ...").pack(anchor="w", pady=(8, 16))

    btns = ttk.Frame(container)
    btns.pack(fill="x", pady=(8,0))

    ttk.Button(btns, text="Choose folder and run", command=lambda: start_flow(root, logo_photo)).pack(side="left")

    ttk.Label(container, text="Tip: Place 'RTH Logo.png' next to this script for branding.\nThe app works even without the logo file.").pack(anchor="w", pady=(16,0))

    center_window(root)
    # Start the flow automatically after the window appears
    root.after(200, lambda: start_flow(root, logo_photo))

    root.mainloop()

if __name__ == "__main__":
    main()

import tkinter as tk
from tkinter import filedialog, messagebox
import PyPDF2
import pyttsx3
import threading
import os
import subprocess
import time

# Initialize GUI window
root = tk.Tk()
root.geometry('500x500')
root.title("Audiobook")

# Variables
vc = tk.IntVar(value=0)
pdf_path = None
rates = {
    "0.5x": 100,   # Half the default speed
    "0.75x": 150,  # Slower than default
    "1x": 200,     # Default speed
    "1.25x": 250,  # Faster than default
    "1.5x": 300    # Even faster
}

def browse():
    global pdf_path
    pdf_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf"), ("All Files", "*.*")])
    if pdf_path:
        path_lbl.config(text=pdf_path)

def save_and_play_audio(speaker, text, save_path):
    try:
        speaker.save_to_file(text, save_path)
        speaker.runAndWait()

        # Ensure the file is completely saved before attempting to open
        time.sleep(1)

        if os.path.exists(save_path):
            if os.name == 'nt':
                os.startfile(save_path)
            elif os.name == 'posix':
                subprocess.call(['open' if sys.platform == 'darwin' else 'xdg-open', save_path])
            load_lbl.config(text="Audio file saved and is now playing.")
        else:
            messagebox.showerror("Error", "Audio file was not saved correctly.")

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")
    finally:
        root.after(1000, lambda: load_lbl.config(text=""))

def read_and_save_audio():
    if not pdf_path:
        messagebox.showwarning("No File Selected", "Please select a PDF file first.")
        return

    try:
        with open(pdf_path, 'rb') as file:
            pdf = PyPDF2.PdfReader(file)
            text = "".join(page.extract_text() for page in pdf.pages if page.extract_text())

        if not text:
            messagebox.showerror("Error", "No text could be extracted from the PDF.")
            return

        speaker = pyttsx3.init()
        voices = speaker.getProperty('voices')
        speaker.setProperty('voice', voices[vc.get()].id)
        selected_rate = rate_choice.get()
        speaker.setProperty('rate', rates[selected_rate])

        save_path = filedialog.asksaveasfilename(defaultextension=".mp3", filetypes=[("MP3 files", "*.mp3")])
        if save_path:
            load_lbl.config(text="Processing...")
            root.update()
            threading.Thread(target=save_and_play_audio, args=(speaker, text, save_path)).start()

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")
    finally:
        root.after(1000, lambda: load_lbl.config(text=""))

def update_rate_lbl(value):
    rate_lbl.config(text=f"Selected Rate: {value}")

# GUI components
title_lbl = tk.Label(root, text="Audiobook Converter", font=("Arial", 24, "bold"), bg="lightblue", pady=10)
title_lbl.pack(fill=tk.X)

path_lbl = tk.Label(root, text="No file selected", font=("Arial", 12))
path_lbl.pack(pady=10)

browse_btn = tk.Button(root, text="Browse a File", command=browse, font=("Arial", 12))
browse_btn.pack(pady=5)

save_btn = tk.Button(root, text="Create and Save the Audio File", command=read_and_save_audio, font=("Arial", 12))
save_btn.pack(pady=5)

voice_frame = tk.Frame(root)
voice_frame.pack(pady=10)

male_rb = tk.Radiobutton(voice_frame, text="Male Voice", variable=vc, value=0, font=("Arial", 12))
male_rb.pack(side=tk.LEFT, padx=10)

female_rb = tk.Radiobutton(voice_frame, text="Female Voice", variable=vc, value=1, font=("Arial", 12))
female_rb.pack(side=tk.LEFT, padx=10)

speed_opts = ["0.5x", "0.75x", "1x", "1.25x", "1.5x"]
rate_choice = tk.StringVar(value="1x")

rate_frame = tk.Frame(root)
rate_frame.pack(pady=10)

tk.Label(rate_frame, text="Speech Rate:", font=("Arial", 12)).pack(anchor='w', padx=20)
speed_menu = tk.OptionMenu(rate_frame, rate_choice, *speed_opts, command=update_rate_lbl)
speed_menu.config(font=("Arial", 12))
speed_menu.pack()

rate_lbl = tk.Label(rate_frame, text=f"Selected Rate: {rate_choice.get()}", font=("Arial", 12))
rate_lbl.pack(pady=5)

load_lbl = tk.Label(root, text="", font=("Arial", 12))
load_lbl.pack(pady=10)

# Start the GUI loop
root.mainloop()

# Mouad Garroud
import os
import re
import tkinter as tk
from tkinter import ttk, messagebox
from yt_dlp import YoutubeDL
import threading
def sanitize_title(title):
    return re.sub(r'[<>:"/\\|?*]', '_', title)
def download_video_mp4(url, output_dir, progress_hook):
    ydl_opts = {
        'format': 'mp4',
        'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
        'progress_hooks': [progress_hook]
    }
    with YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=True)
        return info_dict.get('title', None)
def download_audio_as_mp3(url, video_dir, audio_dir, progress_hook):
    ydl_opts = {
        'format': 'mp4',
        'outtmpl': os.path.join(video_dir, 'video.mp4'),
        'progress_hooks': [progress_hook]
    }
    with YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=True)
        video_title = info_dict.get('title', None)
    if video_title:
        sanitized_title = sanitize_title(video_title)
        input_video_path = os.path.join(video_dir, 'video.mp4')
        renamed_video_path = os.path.join(video_dir, f'{sanitized_title}.mp4')
        output_audio_path = os.path.join(audio_dir, f'{sanitized_title}.mp3')
        if os.path.exists(input_video_path):
            os.rename(input_video_path, renamed_video_path)
            convert_to_mp3(renamed_video_path, output_audio_path)
            os.remove(renamed_video_path)
        else:
            raise FileNotFoundError("Video file not found after download.")
def convert_to_mp3(input_video_path, output_audio_path):
    from moviepy.editor import VideoFileClip
    video = VideoFileClip(input_video_path)
    audio = video.audio
    audio.write_audiofile(output_audio_path)
    audio.close()
    video.close()
def start_download(url, format_choice, progress_label, progress_bar):
    def remove_ansi_escape_codes(text):
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        return ansi_escape.sub('', text)

    def progress_hook(d):
        if d['status'] == 'downloading':
            raw_percent = d.get('_percent_str', '').strip()
            clean_percent = remove_ansi_escape_codes(raw_percent)
            if clean_percent:
                progress_label.config(text=f"{clean_percent}")
            else:
                progress_label.config(text="Downloading...")
            try:
                percentage = float(clean_percent.strip('%')) if clean_percent else 0
                progress_bar['value'] = percentage
            except ValueError:
                progress_label.config(text="Downloading... (progress unavailable)")
            progress_label.update()
            progress_bar.update()
    home_dir = os.path.expanduser("~")
    documents_dir = os.path.join(home_dir, "Documents")
    base_dir = os.path.join(documents_dir, "Downloader")
    video_dir = os.path.join(base_dir, "Video")
    audio_dir = os.path.join(base_dir, "Music")
    os.makedirs(video_dir, exist_ok=True)
    os.makedirs(audio_dir, exist_ok=True)
    try:
        progress_label.config(text="Downloading...")
        if format_choice == 'MP4':
            video_title = download_video_mp4(url, video_dir, progress_hook)
            if video_title:
                messagebox.showinfo("Dowloader", f"Video downloaded as MP4: {video_title}.mp4")
            else:
                messagebox.showerror("Dowloader", "Failed to download video.")
        elif format_choice == 'MP3':
            download_audio_as_mp3(url, video_dir, audio_dir, progress_hook)
            messagebox.showinfo("Dowloader",  "Audio downloaded as .mp3")
        else:
            messagebox.showerror("Dowloader", "Invalid choice. Please select MP3 or MP4.")
    finally:
        progress_label.config(text="")
        progress_bar['value'] = 0
        url_var.set("")
        format_var.set("MP4")
def on_download():
    url = url_var.get().strip()
    format_choice = format_var.get()
    if not url:
        messagebox.showerror("Dowloader", "Please enter a URL.")
        return
    if format_choice not in ['MP3', 'MP4']:
        messagebox.showerror("Dowloader", "Please select a format.")
        return
    download_thread = threading.Thread(target=start_download, args=(url, format_choice, progress_label, progress_bar))
    download_thread.start()
def paste_url():
    url_var.set(root.clipboard_get())
root = tk.Tk()
root.title("Downloader")
root.geometry("410x170")
root.resizable(False, False)
root.iconbitmap('downloader.ico')
icon = tk.PhotoImage(file="downloader.ico")
root.iconphoto(False, icon)
frame = ttk.Frame(root, padding=5)
frame.pack(fill=tk.BOTH, expand=True)
url_var = tk.StringVar()
format_var = tk.StringVar(value="MP4")
url_label = ttk.Label(frame, text="URL :")
url_label.grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
url_entry = ttk.Entry(frame, textvariable=url_var, width=40)
url_entry.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
paste_button = ttk.Button(frame, text="Paste", command=paste_url)
paste_button.grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
format_label = ttk.Label(frame, text="Format:")
format_label.grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
format_frame = ttk.Frame(frame)
format_frame.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
mp3_button = ttk.Radiobutton(format_frame, text="MP3", variable=format_var, value="MP3")
mp3_button.pack(side=tk.LEFT, padx=5)
mp4_button = ttk.Radiobutton(format_frame, text="MP4", variable=format_var, value="MP4")
mp4_button.pack(side=tk.LEFT, padx=5)
download_button = ttk.Button(frame, text="Download", command=on_download)
download_button.grid(row=2, column=0, columnspan=3, pady=5)
progress_label = ttk.Label(frame, text="")
progress_label.grid(row=3, column=0, columnspan=3, pady=5)
progress_bar = ttk.Progressbar(frame, length=400, mode='determinate')
progress_bar.grid(row=4, column=0, columnspan=3, pady=5)
root.mainloop()

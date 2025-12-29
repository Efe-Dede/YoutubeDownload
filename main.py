import customtkinter as ctk
import os
import threading
import re
from pathlib import Path
from yt_dlp import YoutubeDL
from tkinter import messagebox

# App Configuration
ctk.set_appearance_mode("Dark")
ACCENT_COLOR = "#404b62"  # İstediğiniz özel mavi-gri tonu
ACCENT_HOVER = "#4d5b78"
BG_COLOR = "#242424"     # Önceki versiyondaki koyu gri tonu
ENTRY_BG = "#2b2b2b"    # Giriş alanı için hafif açık ton
TEXT_COLOR = "#ffffff"
SECONDARY_TEXT = "#bbbbbb"

class YoutubeDownloaderApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window Config
        self.title("YouTube İndirici - MP3 & MP4")
        self.geometry("600x420")
        self.resizable(False, False)
        self.configure(fg_color=BG_COLOR)

        # Layout Grid Config
        self.grid_columnconfigure(0, weight=1)
        
        # Title
        self.title_label = ctk.CTkLabel(
            self, 
            text="YouTube Video/Ses İndirici", 
            font=ctk.CTkFont(size=26, weight="bold"),
            text_color="white"
        )
        self.title_label.grid(row=0, column=0, padx=20, pady=(30, 20))

        # URL Input
        self.url_entry = ctk.CTkEntry(
            self, 
            placeholder_text="YouTube Linkini Buraya Yapıştırın", 
            width=450,
            height=40,
            fg_color=ENTRY_BG,
            border_color="#3f3f3f",
            text_color="white"
        )
        self.url_entry.grid(row=1, column=0, padx=20, pady=10)

        # Download Button
        self.download_btn = ctk.CTkButton(
            self, 
            text="İNDİR", 
            command=self.start_download_thread, 
            height=45, 
            width=200,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color=ACCENT_COLOR,
            hover_color=ACCENT_HOVER,
            text_color="#ffffff"
        )
        self.download_btn.grid(row=2, column=0, padx=20, pady=(20, 10))

        # Type Selection (MP3/MP4) - Smaller and below button
        self.type_var = ctk.StringVar(value="mp4")
        self.radio_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.radio_frame.grid(row=3, column=0, padx=20, pady=5)
        
        self.radio_mp4 = ctk.CTkRadioButton(
            self.radio_frame, 
            text="MP4 (Video)", 
            variable=self.type_var, 
            value="mp4",
            border_color="#aaaaaa",
            hover_color=ACCENT_COLOR,
            fg_color=ACCENT_COLOR,
            text_color="white",
            font=ctk.CTkFont(size=12)
        )
        self.radio_mp4.grid(row=0, column=0, padx=15, pady=5)
        
        self.radio_mp3 = ctk.CTkRadioButton(
            self.radio_frame, 
            text="MP3 (Ses)", 
            variable=self.type_var, 
            value="mp3",
            border_color="#aaaaaa",
            hover_color=ACCENT_COLOR,
            fg_color=ACCENT_COLOR,
            text_color="white",
            font=ctk.CTkFont(size=12)
        )
        self.radio_mp3.grid(row=0, column=1, padx=15, pady=5)

        # Status & Progress
        self.status_label = ctk.CTkLabel(self, text="Hazır", text_color=SECONDARY_TEXT, font=ctk.CTkFont(size=13, weight="bold"))
        self.status_label.grid(row=4, column=0, padx=20, pady=(15, 5))
        
        self.progress_bar = ctk.CTkProgressBar(
            self, 
            width=450, 
            progress_color=ACCENT_COLOR,
            fg_color="#333333"
        )
        self.progress_bar.grid(row=5, column=0, padx=20, pady=(0, 20))
        self.progress_bar.set(0)

    def start_download_thread(self):
        url = self.url_entry.get()
        if not url:
            messagebox.showerror("Hata", "Lütfen bir YouTube linki girin.")
            return
        
        self.download_btn.configure(state="disabled", text="İndiriliyor...")
        self.status_label.configure(text="İşlem başlıyor...", text_color=ACCENT_COLOR)
        self.progress_bar.set(0)
        
        thread = threading.Thread(target=self.download_content, args=(url,))
        thread.start()

    def progress_hook(self, d):
        if d['status'] == 'downloading':
            try:
                # Use numeric data for smoother progress calculation
                total = d.get('total_bytes') or d.get('total_bytes_estimate')
                downloaded = d.get('downloaded_bytes', 0)
                
                if total:
                    percentage = downloaded / total
                    percent_str = f"{percentage*100:.1f}%"
                else:
                    # Fallback to string parsing if bytes are missing
                    percent_str = d.get('_percent_str', '0%').replace('%', '').strip()
                    percentage = float(percent_str) / 100
                    percent_str = f"{percent_str}%"

                # Clean speed string and remove ANSI color codes using regex
                speed_raw = d.get('_speed_str', '0KB/s').strip()
                # Remove ANSI escape sequences (the weird [0;32m things)
                speed_clean = re.sub(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', '', speed_raw)
                
                # Format speed simply (e.g., 5.25MiB/s -> 5.25 MB)
                speed = speed_clean.replace('iB/s', ' MB').replace('B/s', ' B')
                
                # Also clean percent_str just in case it has codes
                ps_clean = re.sub(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', '', percent_str).replace('%', '').strip()
                
                # Update UI on main thread
                self.after(0, lambda p=percentage, s=speed, ps=ps_clean: 
                           self.update_progress(p, f"%{ps}   İndirme Hızı: {s}"))
            except Exception:
                pass
        elif d['status'] == 'finished':
            self.after(0, lambda: self.update_progress(1.0, "Tamamlandı! İşleniyor...", "#2ecc71"))

    def update_progress(self, value, status_text, color="#aaaaaa"):
        self.status_label.configure(text=status_text, text_color=color)
        self.progress_bar.set(value)

    def download_content(self, url):
        download_type = self.type_var.get()
        output_path = str(Path.home() / "Downloads")
        os.makedirs(output_path, exist_ok=True)

        ydl_opts = {
            'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
            'progress_hooks': [self.progress_hook],
            'noplaylist': True,
            'ffmpeg_location': 'C:/ffmpeg/bin',
            'no_color': True,  # Renk kodlarını kapat
        }

        if download_type == "mp3":
            ydl_opts.update({
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            })
        else:
            ydl_opts.update({
                'format': 'best', 
            })

        try:
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            self.after(0, lambda: self.finish_download(True))
        except Exception as e:
            error_text = str(e)
            self.after(0, lambda msg=error_text: self.finish_download(False, msg))

    def finish_download(self, success, error_msg=""):
        self.download_btn.configure(state="normal", text="İNDİR")
        if success:
            self.status_label.configure(text="İşlem Başarıyla Tamamlandı!", text_color="#2ecc71")
            messagebox.showinfo("Başarılı", "İndirme tamamlandı! İndirilenler klasörünüzü kontrol edin.")
        else:
            self.status_label.configure(text="Hata oluştu.", text_color="#e74c3c")
            messagebox.showerror("Hata", f"İndirme başarısız oldu:\n{error_msg}")

if __name__ == "__main__":
    app = YoutubeDownloaderApp()
    app.mainloop()

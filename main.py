import customtkinter as ctk
import os
import threading
import re
import ctypes
from pathlib import Path
from yt_dlp import YoutubeDL
from tkinter import messagebox
from plyer import notification

# App Configuration
ctk.set_appearance_mode("Dark")
ACCENT_COLOR = "#404b62"
ACCENT_HOVER = "#4d5b78"
BG_COLOR = "#242424"
ENTRY_BG = "#2b2b2b"
TEXT_COLOR = "#ffffff"
SECONDARY_TEXT = "#bbbbbb"

class YoutubeDownloaderApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window Config
        self.title("YouTube İndirici Pro - Gelişmiş")
        self.geometry("700x550") 
        self.resizable(False, False)
        self.configure(fg_color=BG_COLOR)

        self.grid_columnconfigure(0, weight=1)
        
        # Title
        self.title_label = ctk.CTkLabel(self, text="YouTube Video & Ses Kesici", font=ctk.CTkFont(size=26, weight="bold"))
        self.title_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        # --- Link & Control Area ---
        self.input_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.input_frame.grid(row=1, column=0, padx=20, pady=5, sticky="ew")
        self.input_frame.grid_columnconfigure(0, weight=1)

        self.url_entry = ctk.CTkEntry(self.input_frame, placeholder_text="YouTube Linkini Girin", height=45, fg_color=ENTRY_BG, border_color="#3f3f3f")
        self.url_entry.grid(row=0, column=0, padx=(0, 2), sticky="ew")

        # Quality Dropdown (Back to top row)
        self.qualities = ["MP4 - Otomatik (1080p)", "MP4 - 2160p 4K", "MP4 - 1440p 2K", "MP4 - 1080p FHD", "MP4 - 720p HD", "MP4 - 480p SD", "MP3 - Sadece Ses"]
        self.quality_var = ctk.StringVar(value=self.qualities[0])
        self.quality_dropdown = ctk.CTkComboBox(self.input_frame, values=self.qualities, variable=self.quality_var, width=170, height=45)
        self.quality_dropdown.grid(row=0, column=1, padx=(0, 2))

        self.download_btn = ctk.CTkButton(self.input_frame, text="⏎", width=50, height=45, font=ctk.CTkFont(size=24, weight="bold"), fg_color=ACCENT_COLOR, hover_color=ACCENT_HOVER, command=self.start_download_thread)
        self.download_btn.grid(row=0, column=2)

        # --- Quality & Trimming Area ---
        self.settings_frame = ctk.CTkFrame(self, fg_color="#1e1e1e", corner_radius=10)
        self.settings_frame.grid(row=2, column=0, padx=20, pady=15, sticky="nsew")
        
        # Analyze Button (Now in settings area)
        self.check_btn = ctk.CTkButton(self.settings_frame, text="Videoyu Analiz Et", width=150, height=35, fg_color="#2c3e50", hover_color="#34495e", command=self.start_analyze_thread)
        self.check_btn.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")

        # Duration Info
        self.info_label = ctk.CTkLabel(self.settings_frame, text="Süre Bilgisi İçin Analiz Edin", text_color=SECONDARY_TEXT)
        self.info_label.grid(row=0, column=1, padx=20, pady=(20, 10), sticky="e")

        # Trimming Inputs
        self.trim_frame = ctk.CTkFrame(self.settings_frame, fg_color="transparent")
        self.trim_frame.grid(row=1, column=0, columnspan=2, padx=20, pady=(0, 20), sticky="ew")
        
        self.start_label = ctk.CTkLabel(self.trim_frame, text="Başlangıç (sn):")
        self.start_label.pack(side="left", padx=5)
        self.start_entry = ctk.CTkEntry(self.trim_frame, width=80, placeholder_text="0")
        self.start_entry.pack(side="left", padx=5)
        self.start_entry.insert(0, "0")

        self.end_label = ctk.CTkLabel(self.trim_frame, text="Bitiş (sn):")
        self.end_label.pack(side="left", padx=(20, 5))
        self.end_entry = ctk.CTkEntry(self.trim_frame, width=80, placeholder_text="Bitiş")
        self.end_entry.pack(side="left", padx=5)

        self.trim_hint = ctk.CTkLabel(self.settings_frame, text="Tüm videoyu indirmek için bitişi boş bırakın.", font=ctk.CTkFont(size=10), text_color="#666666")
        self.trim_hint.grid(row=2, column=0, columnspan=2, pady=(0, 10))

        # --- Progress & Notification Area ---
        self.status_label = ctk.CTkLabel(self, text="Hazır", text_color=SECONDARY_TEXT, font=ctk.CTkFont(size=13, weight="bold"))
        self.status_label.grid(row=3, column=0, padx=20, pady=(10, 5))
        
        self.progress_bar = ctk.CTkProgressBar(self, width=660, progress_color=ACCENT_COLOR, fg_color="#333333")
        self.progress_bar.grid(row=4, column=0, padx=20, pady=(0, 20))
        self.progress_bar.set(0)

        self._is_running = True
        self.video_duration_seconds = 0

    def start_analyze_thread(self):
        url = self.url_entry.get()
        if not url: return 
        self.check_btn.configure(state="disabled", text="Analiz...")
        threading.Thread(target=self.analyze_video, args=(url,), daemon=True).start()

    def analyze_video(self, url):
        try:
            with YoutubeDL({'quiet': True, 'ffmpeg_location': 'C:/ffmpeg/bin'}) as ydl:
                info = ydl.extract_info(url, download=False)
                duration = info.get('duration', 0)
                title = info.get('title', 'Video')
                self.video_duration_seconds = duration
                
                minutes = duration // 60
                seconds = duration % 60
                duration_str = f"{minutes:02d}:{seconds:02d}"
                
                self.after(0, lambda: self.update_info(duration_str, duration))
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Hata", f"Video analiz edilemedi: {str(e)}"))
        finally:
            self.after(0, lambda: self.check_btn.configure(state="normal", text="Analiz Et"))

    def update_info(self, duration_str, duration):
        self.info_label.configure(text=f"Video Süresi: {duration_str}")
        self.end_entry.delete(0, 'end')
        self.end_entry.insert(0, str(duration))

    def start_download_thread(self):
        url = self.url_entry.get()
        if not url:
            messagebox.showerror("Hata", "Lütfen bir link girin.")
            return
        
        self.download_btn.configure(state="disabled", text="...")
        self.status_label.configure(text="Hazırlanıyor...", text_color=ACCENT_COLOR)
        threading.Thread(target=self.download_content, args=(url,), daemon=True).start()

    def progress_hook(self, d):
        if not self._is_running: return
        if d['status'] == 'downloading':
            try:
                total = d.get('total_bytes') or d.get('total_bytes_estimate')
                downloaded = d.get('downloaded_bytes', 0)
                if total:
                    p = downloaded / total
                    ps = f"{p*100:.1f}"
                else:
                    ps = "???"
                    p = 0
                
                speed_raw = d.get('_speed_str', '0KB/s').strip()
                speed_clean = re.sub(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', '', speed_raw)
                speed = speed_clean.replace('iB/s', ' MB').replace('B/s', ' B')
                
                self.after(0, lambda: self.update_progress(p, f"%{ps}   Hız: {speed}"))
            except: pass
        elif d['status'] == 'finished':
            self.after(0, lambda: self.update_progress(1.0, "İşleniyor (Kesme/Birleştirme)...", "#2ecc71"))

    def update_progress(self, value, text, color="#aaaaaa"):
        self.progress_bar.set(value)
        self.status_label.configure(text=text, text_color=color)

    def download_content(self, url):
        quality = self.quality_var.get()
        start_t = self.start_entry.get().strip() or "0"
        end_t = self.end_entry.get().strip()
        
        output_path = str(Path.home() / "Downloads")
        format_str = "best"
        is_audio = "Ses" in quality
        
        if "2160p" in quality: format_str = "bestvideo[height<=2160]+bestaudio/best"
        elif "1440p" in quality: format_str = "bestvideo[height<=1440]+bestaudio/best"
        elif "1080p" in quality: format_str = "bestvideo[height<=1080]+bestaudio/best"
        elif "720p" in quality: format_str = "bestvideo[height<=720]+bestaudio/best"
        elif "480p" in quality: format_str = "bestvideo[height<=480]+bestaudio/best"
        elif "Ses" in quality: format_str = "bestaudio/best"

        ydl_opts = {
            'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
            'progress_hooks': [self.progress_hook],
            'ffmpeg_location': 'C:/ffmpeg/bin',
            'no_color': True,
            'format': format_str,
            'force_keyframes_at_cuts': True,
        }

        # Handle Trimming (Download Ranges)
        if start_t != "0" or (end_t and end_t != str(self.video_duration_seconds)):
            try:
                s = float(start_t)
                e = float(end_t) if end_t else None
                ydl_opts['download_ranges'] = lambda info_dict, ydl, s=s, e=e: [{'start_time': s, 'end_time': e}]
            except: pass

        if is_audio:
            ydl_opts['postprocessors'] = [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3','preferredquality': '192'}]
        else:
            ydl_opts['merge_output_format'] = 'mp4'

        try:
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            self.after(0, lambda: self.finish_download(True))
        except Exception as e:
            self.after(0, lambda: self.finish_download(False, str(e)))

    def finish_download(self, success, error_msg=""):
        self.download_btn.configure(state="normal", text="↵")
        if success:
            self.status_label.configure(text="Başarıyla Tamamlandı!", text_color="#2ecc71")
            # Notification
            try:
                notification.notify(title='YouTube İndirici', message='İndirme başarıyla tamamlandı!', app_name='YT Pro', timeout=10)
                if os.name == 'nt':
                    ctypes.windll.user32.FlashWindow(self.winfo_id(), True)
            except: pass
        else:
            messagebox.showerror("Hata", f"İndirme başarısız: {error_msg}")

if __name__ == "__main__":
    app = YoutubeDownloaderApp()
    app.mainloop()

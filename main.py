import customtkinter as ctk
import os
import threading
import re
import ctypes
import json
import subprocess
import urllib.request
from pathlib import Path
from yt_dlp import YoutubeDL
from tkinter import messagebox, filedialog
from plyer import notification
from PIL import Image, ImageTk
from io import BytesIO
from datetime import datetime, timedelta
import sys

# --- HELPERS ---
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def find_ffmpeg():
    """ Try to find ffmpeg in common locations or PATH """
    # 1. Check C:/ffmpeg/bin
    if os.path.exists("C:/ffmpeg/bin/ffmpeg.exe"):
        return "C:/ffmpeg/bin"
    # 2. Check current directory
    if os.path.exists("ffmpeg.exe"):
        return os.getcwd()
    # 3. Check if it's in PATH
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
        return None # It's in PATH, no need to specify location
    except:
        return "C:/ffmpeg/bin" # Default fallback

# --- MODERN ELEGANT DESIGN ---
ctk.set_appearance_mode("Dark")
THEME = {
    "bg": "#0F172A",              # Slack-like dark blue
    "sidebar": "#1E293B",         # Slightly lighter sidebar
    "accent": "#6366F1",          # Modern indigo
    "accent_hover": "#4F46E5",   # Deeper indigo
    "text_main": "#F8FAFC",      # Brighter white
    "text_dim": "#94A3B8",       # Slate 400
    "success": "#10B981",        # Emerald
    "error": "#EF4444",          # Red
    "card_bg": "#1E293B",        # Card background
    "border": "#334155",         # Slate 700
}

# --- CUSTOM COMPONENTS ---

class RangeSlider(ctk.CTkCanvas):
    def __init__(self, master, from_, to, command=None, **kwargs):
        super().__init__(master, height=40, bg=THEME["card_bg"], highlightthickness=0, **kwargs)
        self.from_ = from_
        self.to = to
        self.command = command
        
        self.start_val = from_
        self.end_val = to
        
        self.bind("<Configure>", self.draw)
        self.bind("<B1-Motion>", self.on_drag)
        self.bind("<Button-1>", self.on_click)
        
        self.active_thumb = None

    def val_to_x(self, val):
        width = self.winfo_width()
        if width <= 30: return 15
        return 15 + (val - self.from_) / (self.to - self.from_) * (width - 30)

    def x_to_val(self, x):
        width = self.winfo_width()
        if width <= 30: return self.from_
        val = self.from_ + (x - 15) / (width - 30) * (self.to - self.from_)
        return max(self.from_, min(self.to, val))

    def draw(self, event=None):
        self.delete("all")
        w = self.winfo_width()
        h = self.winfo_height()
        if w <= 30: return
        
        track_y = h / 2
        
        # Track background
        self.create_line(15, track_y, w-15, track_y, fill=THEME["border"], width=6, capstyle="round")
        
        # Highlighted Range
        x1 = self.val_to_x(self.start_val)
        x2 = self.val_to_x(self.end_val)
        self.create_line(x1, track_y, x2, track_y, fill=THEME["accent"], width=6, capstyle="round")
        
        # Start Thumb
        self.create_oval(x1-9, track_y-9, x1+9, track_y+9, fill="#FFFFFF", outline=THEME["accent"], width=2)
        # End Thumb
        self.create_oval(x2-9, track_y-9, x2+9, track_y+9, fill="#FFFFFF", outline=THEME["success"], width=2)

    def on_click(self, event):
        x1 = self.val_to_x(self.start_val)
        x2 = self.val_to_x(self.end_val)
        dist_start = abs(event.x - x1)
        dist_end = abs(event.x - x2)
        
        if dist_start < dist_end and dist_start < 20:
            self.active_thumb = "start"
        elif dist_end < 20:
            self.active_thumb = "end"
        else:
            self.active_thumb = None

    def on_drag(self, event):
        if not self.active_thumb: return
        val = self.x_to_val(event.x)
        
        if self.active_thumb == "start":
            if val < self.end_val - (self.to / 100): # Min 1% gap
                self.start_val = val
        else:
            if val > self.start_val + (self.to / 100): # Min 1% gap
                self.end_val = val
            
        self.draw()
        if self.command: self.command(self.start_val, self.end_val)

    def get(self):
        return self.start_val, self.end_val

# --- MAIN APP ---

class DownloaderApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # App Configuration
        self.title("Downloader")
        self.geometry("900x680")
        try:
            self.iconbitmap(resource_path("icon.ico"))
        except:
            pass
        self.configure(fg_color=THEME["bg"])
        
        # State
        self.settings_file = os.path.join(os.path.expanduser("~"), ".downloader_settings.json")
        self.download_path = self.load_settings()
        self.last_downloaded_file = None
        self.download_segment = {"start": 0, "end": 0, "active": False}
        self._alive = True

        # Layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # 1. Sidebar
        self.sidebar = ctk.CTkFrame(self, fg_color=THEME["sidebar"], width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(3, weight=1)

        self.logo_label = ctk.CTkLabel(
            self.sidebar, 
            text="🚀 Downloader", 
            font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold"),
            text_color=THEME["accent"]
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=30)

        self.nav_download_btn = self.create_nav_btn("🚀 İndirici", self.show_download_page, row=1)
        self.nav_settings_btn = self.create_nav_btn("⚙️ Ayarlar", self.show_settings_page, row=2)

        self.version_label = ctk.CTkLabel(self.sidebar, text="v2.1", font=ctk.CTkFont(size=11), text_color=THEME["text_dim"])
        self.version_label.grid(row=4, column=0, pady=20)

        # 2. Main Content Area
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.container.grid_columnconfigure(0, weight=1)
        self.container.grid_rowconfigure(0, weight=1)

        self.pages = {}
        self.init_pages()
        self.show_download_page()

    def create_nav_btn(self, text, command, row):
        btn = ctk.CTkButton(
            self.sidebar,
            text=text,
            command=command,
            fg_color="transparent",
            text_color=THEME["text_dim"],
            hover_color=THEME["border"],
            anchor="w",
            height=45,
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="normal"),
            corner_radius=8
        )
        btn.grid(row=row, column=0, sticky="ew", padx=15, pady=5)
        return btn

    def init_pages(self):
        # Download Page (Scrollable)
        self.download_page = ctk.CTkScrollableFrame(self.container, fg_color="transparent")
        self.pages["download"] = self.download_page
        self.setup_download_page()

        # Settings Page
        self.settings_page = ctk.CTkFrame(self.container, fg_color="transparent")
        self.pages["settings"] = self.settings_page
        self.setup_settings_page()

    def show_page(self, page_name):
        for name, page in self.pages.items():
            if name == page_name:
                page.grid(row=0, column=0, sticky="nsew")
            else:
                page.grid_forget()
        
        # Update button styles
        btns = {
            "download": self.nav_download_btn,
            "settings": self.nav_settings_btn
        }
        for name, btn in btns.items():
            if name == page_name:
                btn.configure(fg_color=THEME["accent"], text_color="#FFFFFF")
            else:
                btn.configure(fg_color="transparent", text_color=THEME["text_dim"])

    def show_download_page(self): self.show_page("download")
    def show_settings_page(self): self.show_page("settings")

    # --- PAGES SETUP ---

    def setup_download_page(self):
        self.download_page.grid_columnconfigure(0, weight=1)
        
        # Header
        header = ctk.CTkLabel(
            self.download_page, 
            text="Video İndirici", 
            font=ctk.CTkFont(family="Segoe UI", size=28, weight="bold"),
            text_color=THEME["text_main"],
            anchor="w"
        )
        header.grid(row=0, column=0, sticky="w", pady=(0, 5))
        
        subheader = ctk.CTkLabel(
            self.download_page, 
            text="YouTube, TikTok ve Instagram'dan zahmetsizce video indirin.", 
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=THEME["text_dim"],
            anchor="w"
        )
        subheader.grid(row=1, column=0, sticky="w", pady=(0, 20))

        # Input Card
        input_card = ctk.CTkFrame(self.download_page, fg_color=THEME["card_bg"], corner_radius=16, border_width=1, border_color=THEME["border"])
        input_card.grid(row=2, column=0, sticky="ew")
        input_card.grid_columnconfigure(0, weight=1)

        self.url_entry = ctk.CTkEntry(
            input_card, 
            placeholder_text="Video bağlantısını buraya yapıştırın...", 
            height=50, 
            fg_color=THEME["bg"], 
            border_color=THEME["border"],
            corner_radius=10,
            font=ctk.CTkFont(size=14)
        )
        self.url_entry.grid(row=0, column=0, padx=20, pady=20, sticky="ew")

        # Controls
        ctrl_frame = ctk.CTkFrame(input_card, fg_color="transparent")
        ctrl_frame.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="ew")
        ctrl_frame.grid_columnconfigure(0, weight=1)

        self.qualities = ["Otomatik (1080p)", "2160p 4K", "1440p 2K", "1080p FHD", "720p HD", "480p SD", "MP3 Sadece Ses"]
        self.quality_var = ctk.StringVar(value=self.qualities[0])
        self.quality_menu = ctk.CTkComboBox(
            ctrl_frame, 
            values=self.qualities, 
            variable=self.quality_var,
            height=45, 
            fg_color=THEME["bg"],
            border_color=THEME["border"],
            state="readonly"
        )
        self.quality_menu.grid(row=0, column=0, sticky="ew", padx=(0, 10))

        self.go_btn = ctk.CTkButton(
            ctrl_frame, 
            text="Analiz Et ve İndir", 
            command=self.start_download_thread, 
            height=45, 
            fg_color=THEME["accent"], 
            hover_color=THEME["accent_hover"],
            font=ctk.CTkFont(weight="bold")
        )
        self.go_btn.grid(row=0, column=1, padx=(10, 0))

        # Status & Progress Area
        self.status_container = ctk.CTkFrame(self.download_page, fg_color="transparent")
        self.status_container.grid(row=3, column=0, sticky="ew", pady=20)
        self.status_container.grid_columnconfigure(0, weight=1)

        self.status_label = ctk.CTkLabel(self.status_container, text="", font=ctk.CTkFont(size=13), text_color=THEME["text_dim"])
        self.status_label.grid(row=0, column=0, pady=(0, 10))

        self.progress_bar = ctk.CTkProgressBar(self.status_container, height=8, corner_radius=4, progress_color=THEME["accent"], fg_color=THEME["border"])
        self.progress_bar.grid(row=1, column=0, sticky="ew")
        self.progress_bar.set(0)

        # Preview Container
        self.preview_container = ctk.CTkFrame(self.download_page, fg_color="transparent")
        self.preview_container.grid(row=4, column=0, sticky="ew")
        self.preview_container.grid_columnconfigure(0, weight=1)
        self.current_preview = None

    def setup_settings_page(self):
        self.settings_page.grid_columnconfigure(0, weight=1)
        
        header = ctk.CTkLabel(self.settings_page, text="Ayarlar", font=ctk.CTkFont(size=24, weight="bold"), text_color=THEME["text_main"])
        header.grid(row=0, column=0, sticky="w", pady=(0, 30))

        # Path Setting
        path_card = ctk.CTkFrame(self.settings_page, fg_color=THEME["card_bg"], corner_radius=12, border_width=1, border_color=THEME["border"])
        path_card.grid(row=1, column=0, sticky="ew", pady=10)
        path_card.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(path_card, text="📁 İndirme Konumu", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=20, pady=(20, 5), sticky="w")
        
        self.path_entry = ctk.CTkEntry(path_card, fg_color=THEME["bg"], border_color=THEME["border"], height=40)
        self.path_entry.grid(row=1, column=0, columnspan=2, padx=20, pady=(0, 20), sticky="ew")
        self.update_path_display()
        
        self.browse_btn = ctk.CTkButton(path_card, text="Değiştir", command=self.browse_folder, width=100, fg_color=THEME["accent"])
        self.browse_btn.grid(row=1, column=2, padx=(0, 20), pady=(0, 20))

    # --- CORE LOGIC ---

    def is_url(self, text):
        url_patterns = [
            r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/',
            r'(https?://)?(www\.)?youtu\.be/',
            r'(https?://)?(www\.)?tiktok\.com/',
            r'(https?://)?(www\.)?instagram\.com/'
        ]
        return any(re.match(pattern, text) for pattern in url_patterns)

    def process_request(self, query):
        try:
            ydl_opts = {'quiet': True, 'no_warnings': True}
            with YoutubeDL(ydl_opts) as ydl:
                if self.is_url(query):
                    self.update_status("Bağlantı analiz ediliyor...", THEME["accent"])
                    info = ydl.extract_info(query, download=False)
                    video_url = query
                else:
                    self.update_status("YouTube'da aranıyor...", THEME["accent"])
                    search_results = ydl.extract_info(f"ytsearch1:{query}", download=False)
                    if not search_results or not search_results.get('entries'): raise Exception("Video bulunamadı")
                    info = search_results['entries'][0]
                    video_url = info['webpage_url']

                self.after(0, lambda: self.show_preview(info, video_url))
                self.update_status("Onay bekleniyor", THEME["text_dim"])
        except Exception as e:
            self.after(0, lambda: self.show_error(str(e)))

    def start_download_thread(self):
        query = self.url_entry.get().strip()
        if not query: return
        self.go_btn.configure(state="disabled")
        if self.current_preview: self.current_preview.destroy()
        threading.Thread(target=self.process_request, args=(query,), daemon=True).start()

    def show_preview(self, info, url):
        if self.current_preview: self.current_preview.destroy()
        
        card = ctk.CTkFrame(self.preview_container, fg_color=THEME["card_bg"], corner_radius=16, border_width=1, border_color=THEME["border"])
        card.pack(fill="x", pady=10)
        self.current_preview = card
        
        card.grid_columnconfigure(1, weight=1)
        
        # Thumbnail
        thumb_frame = ctk.CTkFrame(card, fg_color="black", width=160, height=90, corner_radius=8)
        thumb_frame.grid(row=0, column=0, padx=15, pady=15)
        thumb_frame.grid_propagate(False)
        
        try:
            with urllib.request.urlopen(info.get('thumbnail', ''), timeout=5) as u:
                img = Image.open(BytesIO(u.read()))
                img.thumbnail((160, 90), Image.Resampling.LANCZOS)
                photo = ctk.CTkImage(img, size=(160, 90))
                ctk.CTkLabel(thumb_frame, image=photo, text="").pack()
        except:
            ctk.CTkLabel(thumb_frame, text="🎬", font=ctk.CTkFont(size=30)).pack(expand=True)

        # Info
        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.grid(row=0, column=1, sticky="nsew", pady=15, padx=(0, 15))
        
        title = info.get('title', 'Başlıksız')
        if len(title) > 50: title = title[:47] + "..."
        ctk.CTkLabel(info_frame, text=title, font=ctk.CTkFont(size=15, weight="bold"), anchor="w").pack(fill="x")
        
        uploader = info.get('uploader', info.get('uploader_id', 'Bilinmeyen'))
        ctk.CTkLabel(info_frame, text=f"👤 {uploader}", font=ctk.CTkFont(size=12), text_color=THEME["text_dim"], anchor="w").pack(fill="x")
        
        duration = int(info.get('duration', 0))
        duration_str = self.format_time(duration)
        ctk.CTkLabel(info_frame, text=f"⏱️ {duration_str}", font=ctk.CTkFont(size=12), text_color=THEME["text_dim"], anchor="w").pack(fill="x")

        # Range Slider
        if duration > 0:
            segment_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
            segment_frame.pack(fill="x", pady=10)
            
            self.download_segment = {"start": 0, "end": duration, "active": True}
            
            self.range_label = ctk.CTkLabel(segment_frame, text=f"Seçilen Aralık: {self.format_time(0)} - {self.format_time(duration)}", font=ctk.CTkFont(size=11), text_color=THEME["accent"])
            self.range_label.pack()

            def update_range(s, e):
                self.download_segment["start"] = int(s)
                self.download_segment["end"] = int(e)
                self.range_label.configure(text=f"Seçilen Aralık: {self.format_time(s)} - {self.format_time(e)}")

            self.range_slider = RangeSlider(segment_frame, from_=0, to=duration, command=update_range)
            self.range_slider.pack(fill="x", pady=(5, 0))
        else:
            self.download_segment["active"] = False

        # Actions
        self.preview_btn_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
        self.preview_btn_frame.pack(fill="x", pady=(10, 0))
        
        ctk.CTkButton(self.preview_btn_frame, text="✓ Başlat", width=100, height=32, fg_color=THEME["success"], command=lambda: self.confirm_download(url)).pack(side="left", padx=5)
        ctk.CTkButton(self.preview_btn_frame, text="✕ İptal", width=80, height=32, fg_color=THEME["border"], command=self.cancel_download).pack(side="left", padx=5)

    def confirm_download(self, url):
        self.update_status("İndirme başlatılıyor...", THEME["accent"])
        self.go_btn.configure(state="disabled")
        threading.Thread(target=self.download_core, args=(url,), daemon=True).start()

    def cancel_download(self):
        if self.current_preview: self.current_preview.destroy()
        self.go_btn.configure(state="normal")
        self.update_status("İşlem iptal edildi", THEME["text_dim"])
        self.progress_bar.set(0)

    def download_core(self, url):
        qual = self.quality_var.get()
        audio_only = "Ses" in qual
        fmt = "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best"
        
        if "2160p" in qual: fmt = "bestvideo[height<=2160]+bestaudio/best"
        elif "1440p" in qual: fmt = "bestvideo[height<=1440]+bestaudio/best"
        elif "720p" in qual: fmt = "bestvideo[height<=720]+bestaudio/best"
        elif "Ses" in qual: fmt = "bestaudio/best"

        ffmpeg_path = find_ffmpeg()
        
        # Segment download için geçici dosya kullanacağız
        use_segment = self.download_segment["active"]
        
        opts = {
            'outtmpl': os.path.join(self.download_path, '%(title)s_temp.%(ext)s' if use_segment else '%(title)s.%(ext)s'),
            'progress_hooks': [self.progress_hook],
            'format': fmt,
            'prefer_ffmpeg': True,
        }
        
        if ffmpeg_path:
            opts['ffmpeg_location'] = ffmpeg_path

        if audio_only:
            opts['postprocessors'] = [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3','preferredquality': '320'}]
        else:
            opts['merge_output_format'] = 'mp4'

        try:
            # Adım 1: Videoyu indir
            with YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=True)
                temp_filepath = ydl.prepare_filename(info)
                if audio_only: 
                    temp_filepath = os.path.splitext(temp_filepath)[0] + ".mp3"
                
                # Adım 2: Eğer segment seçildiyse, FFmpeg ile kes
                if use_segment and os.path.exists(temp_filepath):
                    self.after(0, lambda: self.update_progress(0.95, "Video kesiliyor..."))
                    
                    start = self.download_segment["start"]
                    end = self.download_segment["end"]
                    duration = end - start
                    
                    # Final dosya adı
                    final_filepath = temp_filepath.replace("_temp", "")
                    
                    # FFmpeg komutu - videoyu kes
                    ffmpeg_exe = "ffmpeg"
                    if ffmpeg_path:
                        ffmpeg_exe = os.path.join(ffmpeg_path, "ffmpeg.exe")
                    
                    cmd = [
                        ffmpeg_exe,
                        '-i', temp_filepath,
                        '-ss', str(start),
                        '-t', str(duration),
                        '-c', 'copy',  # Re-encode etmeden kes (hızlı)
                        '-y',  # Üzerine yaz
                        final_filepath
                    ]
                    
                    result = subprocess.run(cmd, capture_output=True, text=True)
                    
                    if result.returncode == 0:
                        # Geçici dosyayı sil
                        try:
                            os.remove(temp_filepath)
                        except:
                            pass
                        self.last_downloaded_file = final_filepath
                    else:
                        raise Exception(f"Video kesme hatası: {result.stderr}")
                else:
                    self.last_downloaded_file = temp_filepath
                    
            self.after(0, lambda: self.download_done(True))
        except Exception as e:
            self.after(0, lambda: self.download_done(False, str(e)))

    def progress_hook(self, d):
        if d['status'] == 'downloading':
            tot = d.get('total_bytes') or d.get('total_bytes_estimate') or 1
            cur = d.get('downloaded_bytes', 0)
            p = cur / tot
            speed = d.get('_speed_str', '0KB/s')
            self.after(0, lambda: self.update_progress(p, f"İndiriliyor%{p*100:.1f} İndirme Hızı:{speed}"))
        elif d['status'] == 'finished':
            self.after(0, lambda: self.update_progress(1.0, "Dönüştürülüyor..."))

    def update_progress(self, val, text):
        self.progress_bar.set(val)
        self.status_label.configure(text=text)

    def download_done(self, success, err=""):
        self.go_btn.configure(state="normal")
        if success:
            self.update_status("Tamamlandı! 🎉", THEME["success"])
            notification.notify(title="İndirme Tamamlandı", message="Dosya başarıyla kaydedildi.", timeout=3)
            self.show_completion_options()
        else:
            self.update_status("Hata oluştu", THEME["error"])
            messagebox.showerror("Hata", f"İndirme başarısız: {err}")

    def show_completion_options(self):
        if hasattr(self, 'preview_btn_frame') and self.preview_btn_frame.winfo_exists():
            for b in self.preview_btn_frame.winfo_children(): b.destroy()
            ctk.CTkButton(self.preview_btn_frame, text="📂 Dosyayı Göster", command=self.open_last_file).pack(side="left", padx=5)
            ctk.CTkButton(self.preview_btn_frame, text="Kapat", command=self.cancel_download, fg_color=THEME["border"]).pack(side="left", padx=5)

    def open_last_file(self):
        if self.last_downloaded_file and os.path.exists(self.last_downloaded_file):
            if os.name == 'nt': subprocess.run(['explorer', '/select,', self.last_downloaded_file])
            else: subprocess.run(['open', os.path.dirname(self.last_downloaded_file)])

    def load_settings(self):
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    return json.load(f).get('download_path', str(Path.home() / "Downloads"))
        except: pass
        return str(Path.home() / "Downloads")

    def save_settings(self):
        with open(self.settings_file, 'w') as f:
            json.dump({'download_path': self.download_path}, f)

    def browse_folder(self):
        folder = filedialog.askdirectory(initialdir=self.download_path)
        if folder:
            self.download_path = folder
            self.update_path_display()
            self.save_settings()

    def update_path_display(self):
        self.path_entry.configure(state="normal")
        self.path_entry.delete(0, "end")
        self.path_entry.insert(0, self.download_path)
        self.path_entry.configure(state="readonly")

    def format_time(self, seconds):
        if seconds < 3600:
            return f"{int(seconds)//60:02d}:{int(seconds)%60:02d}"
        return str(timedelta(seconds=int(seconds)))

    def update_status(self, text, color):
        self.status_label.configure(text=text, text_color=color)

    def show_error(self, msg):
        self.update_status("Hata oluştu", THEME["error"])
        self.go_btn.configure(state="normal")
        messagebox.showerror("Hata", msg)

if __name__ == "__main__":
    app = DownloaderApp()
    app.mainloop()

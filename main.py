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
from datetime import datetime

import sys

# ... (imports)

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# --- MODERN ELEGANT DESIGN ---
ctk.set_appearance_mode("Dark")
THEME = {
    "bg": "#0A0E1A",              # Deep midnight blue-black
    "accent": "#6366F1",          # Modern indigo
    "accent_hover": "#4F46E5",   # Deeper indigo
    "accent_gradient": "#8B5CF6", # Purple accent for gradients
    "text_main": "#F1F5F9",      # Soft white
    "text_dim": "#94A3B8",       # Muted slate
    "success": "#10B981",        # Modern emerald
    "success_hover": "#059669",  # Deeper emerald
    "error": "#EF4444",          # Keep modern red
    "input_bg": "#1E293B",       # Slate 800
    "card_bg": "#1E293B",        # Rich slate
    "card_border": "#334155",    # Slate 700
    "button_dark": "#334155",    # Slate 700
    "button_hover": "#475569"    # Slate 600
}

class YoutubeDownloaderApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Settings file path
        self.settings_file = os.path.join(os.path.expanduser("~"), ".youtube_downloader_settings.json")
        self.download_path = self.load_settings()
        self.last_downloaded_file = None
        self.current_video_info = None
        self.pending_download_url = None

        # Window Setup
        self.title("Youtube Downloader")
        try:
            self.iconbitmap(resource_path("icon.ico"))
        except:
            pass
        self.geometry("720x680")
        self.resizable(False, False)
        self.configure(fg_color=THEME["bg"])
        
        # Center grid configuration
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Main Container (Centered)
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=25, pady=20)
        
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure((0, 5), weight=0) # Compact layout

        # 1. Header Section
        self.header_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, pady=(5, 15))
        
        self.header_label = ctk.CTkLabel(
            self.header_frame, 
            text="Youtube Downloader", 
            font=ctk.CTkFont(family="Segoe UI", size=26, weight="bold"),
            text_color=THEME["text_main"]
        )
        self.header_label.pack()
        
        self.subheader_label = ctk.CTkLabel(
            self.header_frame, 
            text="Modern video indirme deneyimi", 
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="normal"),
            text_color=THEME["text_dim"]
        )
        self.subheader_label.pack(pady=(3, 0))

        # 2. Input Section
        self.input_parent = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.input_parent.grid(row=1, column=0, sticky="ew", padx=40)
        self.input_parent.grid_columnconfigure(0, weight=1)

        # URL Entry
        self.url_entry = ctk.CTkEntry(
            self.input_parent, 
            placeholder_text="YouTube bağlantısı veya video ismi yazın...", 
            height=48, 
            fg_color=THEME["input_bg"], 
            border_color=THEME["card_border"], 
            border_width=2,
            corner_radius=12,
            font=ctk.CTkFont(family="Segoe UI", size=13),
            placeholder_text_color=THEME["text_dim"],
            text_color=THEME["text_main"]
        )
        self.url_entry.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 12))

        # Controls Row
        self.controls_frame = ctk.CTkFrame(self.input_parent, fg_color="transparent")
        self.controls_frame.grid(row=1, column=0, columnspan=2, sticky="ew")
        self.controls_frame.grid_columnconfigure((0, 1), weight=1) # Equal split

        # Quality Select
        self.qualities = ["Otomatik (1080p)", "2160p 4K", "1440p 2K", "1080p FHD", "720p HD", "480p SD", "MP3 Sadece Ses"]
        self.quality_var = ctk.StringVar(value=self.qualities[0])
        self.quality_menu = ctk.CTkComboBox(
            self.controls_frame, 
            values=self.qualities, 
            variable=self.quality_var,
            height=44, 
            fg_color=THEME["card_bg"],
            border_color=THEME["card_border"],
            button_color=THEME["button_dark"],
            button_hover_color=THEME["button_hover"],
            border_width=2,
            corner_radius=10,
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="normal"),
            dropdown_font=ctk.CTkFont(family="Segoe UI", size=12),
            dropdown_fg_color=THEME["card_bg"],
            dropdown_hover_color=THEME["button_dark"],
            dropdown_text_color=THEME["text_main"],
            text_color=THEME["text_main"],
            state="readonly"
        )
        self.quality_menu.grid(row=0, column=0, sticky="ew", padx=(0, 8))

        # Action Button
        self.go_btn = ctk.CTkButton(
            self.controls_frame, 
            text="İndirmeyi Başlat", 
            command=self.start_download_thread, 
            height=44, 
            fg_color=THEME["accent"], 
            hover_color=THEME["accent_hover"], 
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            corner_radius=10,
            text_color="#FFFFFF"
        )
        self.go_btn.grid(row=0, column=1, sticky="ew", padx=(8, 0))

        # 2.5. Download Location Section
        self.location_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.location_frame.grid(row=2, column=0, sticky="ew", padx=40, pady=(15, 0))
        self.location_frame.grid_columnconfigure(0, weight=1)

        # Location label
        self.location_label = ctk.CTkLabel(
            self.location_frame,
            text="İndirme Konumu:",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="normal"),
            text_color=THEME["text_dim"],
            anchor="w"
        )
        self.location_label.grid(row=0, column=0, sticky="w", pady=(0, 6))

        # Location display and buttons
        self.location_controls = ctk.CTkFrame(self.location_frame, fg_color="transparent")
        self.location_controls.grid(row=1, column=0, sticky="ew")
        self.location_controls.grid_columnconfigure(0, weight=1)

        # Path display
        self.path_display = ctk.CTkEntry(
            self.location_controls,
            height=38,
            fg_color=THEME["card_bg"],
            border_color=THEME["card_border"],
            border_width=2,
            corner_radius=10,
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=THEME["text_main"],
            state="readonly"
        )
        self.path_display.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        self.update_path_display()

        # Browse button
        self.browse_btn = ctk.CTkButton(
            self.location_controls,
            text="📁 Gözat",
            command=self.browse_folder,
            height=38,
            width=90,
            fg_color=THEME["button_dark"],
            hover_color=THEME["button_hover"],
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="normal"),
            corner_radius=10,
            text_color=THEME["text_main"]
        )
        self.browse_btn.grid(row=0, column=1, padx=(0, 8))

        # Open folder button
        self.open_folder_btn = ctk.CTkButton(
            self.location_controls,
            text="📂 Aç",
            command=self.open_download_folder,
            height=38,
            width=70,
            fg_color=THEME["button_dark"],
            hover_color=THEME["button_hover"],
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="normal"),
            corner_radius=10,
            text_color=THEME["text_main"]
        )
        self.open_folder_btn.grid(row=0, column=2)

        # 2.7. Preview/Completion Card Section (Dynamic)
        self.card_container = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.card_container.grid(row=3, column=0, sticky="ew", padx=40, pady=(15, 0))
        self.card_container.grid_columnconfigure(0, weight=1)
        self.preview_card = None
        self.completion_card = None

        # 3. Status Section
        self.status_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.status_frame.grid(row=4, column=0, pady=(15, 10))
        
        self.status = ctk.CTkLabel(
            self.status_frame, 
            text="İndirme yapmak için hazırım", 
            font=ctk.CTkFont(family="Segoe UI", size=12), 
            text_color=THEME["text_dim"]
        )
        self.status.pack(pady=(0, 8))
        
        self.bar = ctk.CTkProgressBar(
            self.status_frame, 
            width=450, 
            height=6, 
            progress_color=THEME["accent"], 
            fg_color=THEME["card_bg"], 
            corner_radius=3
        )
        self.bar.pack()
        self.bar.set(0)


        self._alive = True

    # --- SETTINGS MANAGEMENT ---

    def load_settings(self):
        """Load settings from file or return default download path"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    path = settings.get('download_path', str(Path.home() / "Downloads"))
                    # Verify path exists
                    if os.path.exists(path):
                        return path
        except Exception:
            pass
        return str(Path.home() / "Downloads")

    def save_settings(self):
        """Save current settings to file"""
        try:
            settings = {
                'download_path': self.download_path
            }
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2)
        except Exception:
            pass

    def browse_folder(self):
        """Open folder browser dialog"""
        folder = filedialog.askdirectory(
            title="İndirme Klasörünü Seçin",
            initialdir=self.download_path
        )
        if folder:
            self.download_path = folder
            self.update_path_display()
            self.save_settings()
            self.status.configure(
                text=f"İndirme konumu güncellendi",
                text_color=THEME["success"]
            )

    def update_path_display(self):
        """Update the path display entry"""
        self.path_display.configure(state="normal")
        self.path_display.delete(0, "end")
        self.path_display.insert(0, self.download_path)
        self.path_display.configure(state="readonly")

    def open_download_folder(self):
        """Open the download folder in file explorer"""
        try:
            if os.path.exists(self.download_path):
                if os.name == 'nt':  # Windows
                    os.startfile(self.download_path)
                elif os.name == 'posix':  # macOS and Linux
                    subprocess.call(['open' if sys.platform == 'darwin' else 'xdg-open', self.download_path])
                self.status.configure(
                    text="Klasör açıldı",
                    text_color=THEME["text_dim"]
                )
            else:
                messagebox.showwarning("Uyarı", "İndirme klasörü bulunamadı!")
        except Exception as e:
            messagebox.showerror("Hata", f"Klasör açılamadı: {str(e)}")

    # --- CARD MANAGEMENT ---

    def hide_all_cards(self):
        """Hide all cards"""
        if self.preview_card:
            self.preview_card.grid_forget()
            self.preview_card = None
        if self.completion_card:
            self.completion_card.grid_forget()
            self.completion_card = None

    def show_preview_card(self, video_info, video_url):
        """Show video preview card with thumbnail and info"""
        self.hide_all_cards()
        
        # Create card frame
        self.preview_card = ctk.CTkFrame(
            self.card_container,
            fg_color=THEME["card_bg"],
            corner_radius=16,
            border_width=2,
            border_color=THEME["card_border"]
        )
        self.preview_card.grid(row=0, column=0, sticky="ew", pady=(0, 0))
        self.preview_card.grid_columnconfigure(1, weight=1)

        # Thumbnail section
        thumbnail_frame = ctk.CTkFrame(self.preview_card, fg_color="transparent", width=140)
        thumbnail_frame.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")
        thumbnail_frame.grid_propagate(False)

        # Try to load thumbnail
        try:
            thumbnail_url = video_info.get('thumbnail', '')
            if thumbnail_url:
                # Download thumbnail
                with urllib.request.urlopen(thumbnail_url, timeout=5) as url:
                    img_data = url.read()
                img = Image.open(BytesIO(img_data))
                
                # Resize maintaining aspect ratio
                img.thumbnail((120, 68), Image.Resampling.LANCZOS)
                photo = ctk.CTkImage(light_image=img, dark_image=img, size=(120, 68))
                
                thumbnail_label = ctk.CTkLabel(
                    thumbnail_frame,
                    image=photo,
                    text=""
                )
                thumbnail_label.image = photo  # Keep reference
                thumbnail_label.pack(expand=True)
        except:
            # Fallback if thumbnail fails
            thumbnail_label = ctk.CTkLabel(
                thumbnail_frame,
                text="🎬",
                font=ctk.CTkFont(size=48),
                text_color=THEME["text_dim"]
            )
            thumbnail_label.pack(expand=True)

        # Info section
        info_frame = ctk.CTkFrame(self.preview_card, fg_color="transparent")
        info_frame.grid(row=0, column=1, padx=(0, 15), pady=15, sticky="nsew")
        info_frame.grid_columnconfigure(0, weight=1)

        # Title
        title = video_info.get('title', 'Bilinmeyen')
        if len(title) > 60:
            title = title[:60] + "..."
        title_label = ctk.CTkLabel(
            info_frame,
            text=title,
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=THEME["text_main"],
            anchor="w",
            justify="left"
        )
        title_label.grid(row=0, column=0, sticky="w", pady=(0, 6))

        # Channel
        channel = video_info.get('uploader', 'Bilinmeyen')
        channel_label = ctk.CTkLabel(
            info_frame,
            text=f"📺 {channel}",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=THEME["text_dim"],
            anchor="w"
        )
        channel_label.grid(row=1, column=0, sticky="w", pady=(0, 4))

        # Duration
        duration = video_info.get('duration', 0)
        minutes = duration // 60
        seconds = duration % 60
        duration_str = f"{minutes}:{seconds:02d}"
        
        # Views
        views = video_info.get('view_count', 0)
        if views >= 1000000:
            views_str = f"{views/1000000:.1f}M"
        elif views >= 1000:
            views_str = f"{views/1000:.1f}K"
        else:
            views_str = str(views)

        meta_label = ctk.CTkLabel(
            info_frame,
            text=f"⏱️ {duration_str}  •  👁️ {views_str} görüntülenme",
            font=ctk.CTkFont(family="Segoe UI", size=10),
            text_color=THEME["text_dim"],
            anchor="w"
        )
        meta_label.grid(row=2, column=0, sticky="w", pady=(0, 12))

        # Action buttons
        button_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
        button_frame.grid(row=3, column=0, sticky="w")

        confirm_btn = ctk.CTkButton(
            button_frame,
            text="✓ İndir",
            command=lambda: self.confirm_download(video_url),
            height=34,
            width=100,
            fg_color=THEME["success"],
            hover_color=THEME["success_hover"],
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            corner_radius=10,
            text_color="#FFFFFF"
        )
        confirm_btn.grid(row=0, column=0, padx=(0, 8))

        cancel_btn = ctk.CTkButton(
            button_frame,
            text="✕ İptal",
            command=self.cancel_download,
            height=34,
            width=90,
            fg_color=THEME["button_dark"],
            hover_color=THEME["error"],
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="normal"),
            corner_radius=10,
            text_color=THEME["text_main"]
        )
        cancel_btn.grid(row=0, column=1)

    def show_completion_card(self, filepath):
        """Show download completion card"""
        self.hide_all_cards()
        
        # Create card frame
        self.completion_card = ctk.CTkFrame(
            self.card_container,
            fg_color=THEME["card_bg"],
            corner_radius=16,
            border_width=2,
            border_color=THEME["success"]
        )
        self.completion_card.grid(row=0, column=0, sticky="ew", pady=(0, 0))
        self.completion_card.grid_columnconfigure(0, weight=1)

        # Content frame
        content_frame = ctk.CTkFrame(self.completion_card, fg_color="transparent")
        content_frame.grid(row=0, column=0, padx=20, pady=18, sticky="ew")
        content_frame.grid_columnconfigure(0, weight=1)

        # Success icon and message
        icon_label = ctk.CTkLabel(
            content_frame,
            text="✓",
            font=ctk.CTkFont(family="Segoe UI", size=40, weight="bold"),
            text_color=THEME["success"]
        )
        icon_label.grid(row=0, column=0, pady=(0, 8))

        success_label = ctk.CTkLabel(
            content_frame,
            text="İndirme Başarıyla Tamamlandı!",
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            text_color=THEME["success"]
        )
        success_label.grid(row=1, column=0, pady=(0, 6))

        # Filename
        filename = os.path.basename(filepath)
        if len(filename) > 50:
            filename = filename[:47] + "..."
        file_label = ctk.CTkLabel(
            content_frame,
            text=filename,
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=THEME["text_dim"]
        )
        file_label.grid(row=2, column=0, pady=(0, 15))

        # Action buttons
        button_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        button_frame.grid(row=3, column=0)

        open_file_btn = ctk.CTkButton(
            button_frame,
            text="📂 Dosyayı Göster",
            command=lambda: self.open_file_location(filepath),
            height=36,
            width=140,
            fg_color=THEME["accent"],
            hover_color=THEME["accent_hover"],
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            corner_radius=10,
            text_color="#FFFFFF"
        )
        open_file_btn.grid(row=0, column=0, padx=(0, 8))

        close_btn = ctk.CTkButton(
            button_frame,
            text="Tamam",
            command=self.hide_all_cards,
            height=36,
            width=90,
            fg_color=THEME["button_dark"],
            hover_color=THEME["button_hover"],
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="normal"),
            corner_radius=10,
            text_color=THEME["text_main"]
        )
        close_btn.grid(row=0, column=1)

    def confirm_download(self, video_url):
        """User confirmed download from preview"""
        self.hide_all_cards()
        self.status.configure(text="İndirme başlatılıyor...", text_color=THEME["accent"])
        threading.Thread(target=self.download_core, args=(video_url,), daemon=True).start()

    def cancel_download(self):
        """User cancelled download from preview"""
        self.hide_all_cards()
        self.go_btn.configure(state="normal", text="İndirmeyi Başlat")
        self.status.configure(text="İndirme iptal edildi", text_color=THEME["text_dim"])
        self.bar.set(0)


    # --- LOGIC ---

    def is_youtube_url(self, text):
        """Check if the input is a valid YouTube URL"""
        youtube_patterns = [
            r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/',
            r'(https?://)?(www\.)?youtu\.be/'
        ]
        return any(re.match(pattern, text) for pattern in youtube_patterns)

    def process_video_request(self, query):
        """Analyze input (URL or Search) and show preview card"""
        try:
            ydl_opts = {
                'quiet': True, 
                'no_warnings': True,
            }
            
            with YoutubeDL(ydl_opts) as ydl:
                if self.is_youtube_url(query):
                    # Direct URL
                    self.after(0, lambda: self.status.configure(text="Bağlantı analiz ediliyor...", text_color=THEME["accent"]))
                    info = ydl.extract_info(query, download=False)
                    video_url = query
                else:
                    # Search
                    self.after(0, lambda: self.status.configure(text="YouTube'da aranıyor...", text_color=THEME["accent"]))
                    search_results = ydl.extract_info(f"ytsearch1:{query}", download=False)
                    if not search_results or 'entries' not in search_results or not search_results['entries']:
                        raise Exception("Video bulunamadı")
                    
                    video_id = search_results['entries'][0]['id']
                    video_url = f"https://www.youtube.com/watch?v={video_id}"
                    
                    # Get full info
                    info = ydl.extract_info(video_url, download=False)

                # Show preview
                self.after(0, lambda: self.show_preview_card(info, video_url))
                self.after(0, lambda: self.status.configure(text="İndirme onayı bekleniyor...", text_color=THEME["text_dim"]))
                
        except Exception as e:
            self.after(0, lambda msg=str(e): self.show_error(msg))

    def start_download_thread(self):
        query = self.url_entry.get().strip()
        if not query: return
        
        self.go_btn.configure(state="disabled", text="İşleniyor...")
        self.bar.set(0)
        self.hide_all_cards()
        
        threading.Thread(target=self.process_video_request, args=(query,), daemon=True).start()

    def progress_hook(self, d):
        if not self._alive: return
        if d['status'] == 'downloading':
            try:
                tot = d.get('total_bytes') or d.get('total_bytes_estimate')
                cur = d.get('downloaded_bytes', 0)
                p = cur / (tot if tot else 1)
                sp_raw = d.get('_speed_str', '0KB/s').strip()
                sp = re.sub(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', '', sp_raw).replace('iB/s', ' MB')
                pct = f"{p*100:.1f}"
                self.after(0, lambda v=p, t=f"%{pct}  •  {sp}": self.update_ui(v, t))
            except: pass
        elif d['status'] == 'finished':
            self.after(0, lambda: self.update_ui(1.0, "Dönüştürme işlemi yapılıyor...", THEME["success"]))

    def update_ui(self, val, txt, color=None):
        if not color: color = THEME["text_dim"]
        self.bar.set(val)
        self.status.configure(text=txt, text_color=color)

    def download_core(self, url):
        qual = self.quality_var.get()
        out_path = self.download_path
        
        # Default format: ensure both video and audio are downloaded
        fmt = "bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best"
        audio_only = "Ses" in qual
        
        if "2160p" in qual: 
            fmt = "bestvideo[height<=2160][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=2160]+bestaudio/best"
        elif "1440p" in qual: 
            fmt = "bestvideo[height<=1440][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=1440]+bestaudio/best"
        elif "1080p" in qual: 
            fmt = "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=1080]+bestaudio/best"
        elif "720p" in qual: 
            fmt = "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=720]+bestaudio/best"
        elif "480p" in qual:
            fmt = "bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=480]+bestaudio/best"
        elif "Ses" in qual: 
            fmt = "bestaudio/best"

        opts = {
            'outtmpl': os.path.join(out_path, '%(title)s.%(ext)s'),
            'progress_hooks': [self.progress_hook],
            'ffmpeg_location': 'C:/ffmpeg/bin',
            'no_color': True,
            'format': fmt,
        }

        if audio_only:
            opts['postprocessors'] = [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3','preferredquality': '320'}]
        else:
            # Ensure video and audio are properly merged
            opts['merge_output_format'] = 'mp4'
            opts['postprocessors'] = [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4',
            }]

        try:
            with YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=True)
                self.current_video_info = info  # Save info for history
                
                # Get the actual filename
                if 'requested_downloads' in info:
                    self.last_downloaded_file = info['requested_downloads'][0]['filepath']
                else:
                    # Construct filename from template
                    filename = ydl.prepare_filename(info)
                    self.last_downloaded_file = filename
            self.after(0, lambda: self.download_done(True))
        except Exception as e:
            self.after(0, lambda msg=str(e): self.download_done(False, msg))

    def download_done(self, success, err=""):
        self.go_btn.configure(state="normal", text="İndirmeyi Başlat")
        if success:
            self.status.configure(text="İndirme Tamamlandı! 🎉", text_color=THEME["success"])
            try:
                notification.notify(title='Youtube Downloader', message='Dosya başarıyla indirildi.', timeout=3)
                if os.name == 'nt': ctypes.windll.user32.FlashWindow(self.winfo_id(), True)
            except: pass
            
            # Show in-app completion card
            if self.last_downloaded_file and os.path.exists(self.last_downloaded_file):
                self.show_completion_card(self.last_downloaded_file)
        else:
            self.status.configure(text="Hata Oluştu", text_color=THEME["error"])
            messagebox.showerror("Hata", f"İşlem başarısız: {err}")

    def open_file_location(self, filepath):
        """Open file location and select the file"""
        try:
            if os.name == 'nt':  # Windows
                subprocess.run(['explorer', '/select,', filepath])
            elif sys.platform == 'darwin':  # macOS
                subprocess.run(['open', '-R', filepath])
            else:  # Linux
                subprocess.run(['xdg-open', os.path.dirname(filepath)])
        except Exception as e:
            # Fallback to opening just the folder
            try:
                folder = os.path.dirname(filepath)
                if os.name == 'nt':
                    os.startfile(folder)
                else:
                    subprocess.call(['open' if sys.platform == 'darwin' else 'xdg-open', folder])
            except:
                messagebox.showerror("Hata", f"Dosya konumu açılamadı: {str(e)}")

if __name__ == "__main__":
    app = YoutubeDownloaderApp()
    app.mainloop()

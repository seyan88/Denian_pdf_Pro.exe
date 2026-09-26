"""
Denian Media Pro (GUI)
A bulletproof desktop wrapper for QPDF, Ghostscript, and FFmpeg.
Supports Batch Processing, Real-time Video Progress, Skip Exists, and Split Views.
UI Refactored with Skeuomorphism/Neumorphism principles.
Highly Optimized for Resize Performance.
"""

import os
import sys
import threading
import subprocess
import re
import json
import webbrowser
import tkinter as tk  # Digunakan untuk lightweight structural frames (Optimasi FPS)
from tkinter import filedialog, messagebox
import customtkinter as ctk
from tkinterdnd2 import TkinterDnD, DND_FILES
from PIL import Image  # Untuk memuat gambar Kucing Hitam


def resource_path(relative_path: str) -> str:
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(base_path, relative_path)

def format_file_size(size_in_bytes: int) -> str:
    if size_in_bytes < 1024:
        return f"{size_in_bytes} B"
    elif size_in_bytes < 1024 * 1024:
        return f"{size_in_bytes / 1024:.2f} KB"
    else:
        return f"{size_in_bytes / (1024 * 1024):.2f} MB"


class DenianMediaProApp(ctk.CTk, TkinterDnD.DnDWrapper):

    # --- UI THEME CONSTANTS (Neumorphism / Physical Look) ---
    BG_BASE = "#262626"        # Machined dark base
    PANEL_RAISED = "#333333"   # Raised control panels
    BORDER_RAISED = "#4A4A4A"  # Edge highlight for raised
    PANEL_SUNKEN = "#1A1A1A"   # Deep well for dropzone
    BORDER_SUNKEN = "#111111"  # Inner shadow effect
    LIST_BG = "#181818"        # Latar belakang scrollable frame
    
    BTN_PRIMARY = "#0277BD"
    BTN_PRIMARY_BORDER = "#29B6F6"
    BTN_PRIMARY_HOVER = "#01579B"
    
    BTN_DANGER = "#C62828"
    BTN_DANGER_BORDER = "#EF9A9A"
    BTN_DANGER_HOVER = "#8E0000"
    
    BTN_SUCCESS = "#2E7D32"
    BTN_SUCCESS_BORDER = "#81C784"
    BTN_SUCCESS_HOVER = "#1B5E20"

    def __init__(self):
        super().__init__()
        self.TkdndVersion = TkinterDnD._require(self)

        # State Variables
        self.output_directory: str = ""
        self.is_processing: bool = False
        self.is_cancelled: bool = False
        self.current_process = None
        
        self.tabs_list = ["📄 PDF", "🖼️ Foto", "🎞️ Video"]
        self.file_queues = {t: [] for t in self.tabs_list}
        self.prev_status = "Status: Siap"
        self.current_tab_name = self.tabs_list[0]

        # Configs - Minimal Window Size Optimization
        self.title("Denian Media Pro")
        try:
            self.iconbitmap(resource_path("assets/logo.ico"))
        except:
            pass
        self.geometry("820x940")
        self.minsize(760, 850) # Melindungi dari kerusakan UI saat resize ekstrem

        ctk.set_appearance_mode("Dark")
        self.configure(fg_color=self.BG_BASE)

        self._build_ui()
        self._set_active_tab(self.tabs_list[0])
        self._check_first_run()

    # ==================== UI BUILDING & REFACTORING ====================

    def _build_ui(self):
        self.main_container = ctk.CTkFrame(self, fg_color=self.BG_BASE)
        self.main_container.pack(fill="both", expand=True, padx=24, pady=24)

        self._build_header()
        self._build_tabs()
        
        # Pack bottom-up to handle resizing gracefully
        self._build_actions()
        self._build_progress_status()
        self._build_settings()
        
        # Packed last with expand=True so it takes middle space
        self._build_dropzone()

    def _build_header(self):
        # Menggunakan tk.Frame native untuk container transparan (Menghemat kalkulasi Canvas)
        self.header_frame = tk.Frame(self.main_container, bg=self.BG_BASE)
        self.header_frame.pack(side="top", fill="x", pady=(0, 10))
        
        self.header_title = ctk.CTkLabel(self.header_frame, text="DENIAN MEDIA PRO", font=ctk.CTkFont(size=28, weight="bold", family="Consolas"), text_color="#E0E0E0")
        self.header_title.pack(pady=(5, 0))
        
        self.header_subtitle = ctk.CTkLabel(self.header_frame, text="Kompresi Massal • Kualitas Optimal • Physical Interface", font=ctk.CTkFont(size=14), text_color="#888888")
        self.header_subtitle.pack(pady=(0, 5))

    def _build_tabs(self):
        self.tab_container = ctk.CTkFrame(self.main_container, fg_color=self.PANEL_RAISED, border_color=self.BORDER_RAISED, border_width=2, corner_radius=10)
        self.tab_container.pack(side="top", fill="x", pady=10)
        
        self.tab_btn_wrapper = tk.Frame(self.tab_container, bg=self.PANEL_RAISED)
        self.tab_btn_wrapper.pack(side="top", fill="x", pady=(20, 10))
        
        self.tab_btn_center = tk.Frame(self.tab_btn_wrapper, bg=self.PANEL_RAISED)
        self.tab_btn_center.pack(anchor="center")
        
        self.tab_buttons = {}
        self.tab_frames = {}
        
        self.content_container = tk.Frame(self.tab_container, bg=self.PANEL_SUNKEN)
        self.content_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        for t in self.tabs_list:
            btn = ctk.CTkButton(
                self.tab_btn_center, text=t, 
                font=ctk.CTkFont(size=18, weight="bold"), height=50, width=180, 
                corner_radius=8, border_width=2, 
                command=lambda name=t: self._set_active_tab(name)
            )
            btn.pack(side="left", padx=15)
            self.tab_buttons[t] = btn
            
            f = tk.Frame(self.content_container, bg=self.PANEL_SUNKEN)
            self.tab_frames[t] = f
            
        self.pdf_mode_var = ctk.StringVar(value="Aman (Tanpa Blur / Lossless)")
        self.foto_level_var = ctk.StringVar(value="Seimbang")
        self.foto_ext_var = ctk.StringVar(value=".webp")
        self.video_level_var = ctk.StringVar(value="Seimbang")
        self.video_ext_var = ctk.StringVar(value=".mp4")

        self._build_tab_content(self.tab_frames["📄 PDF"], [("Level Kompresi:", self.pdf_mode_var, ["Aman (Tanpa Blur / Lossless)", "Ekstrem (Ukuran Terkecil)"])])
        self._build_tab_content(self.tab_frames["🖼️ Foto"], [("Level Kompresi:", self.foto_level_var, ["Kualitas Tinggi", "Seimbang", "Ekstrem"]), ("Format Output:", self.foto_ext_var, [".webp", ".jpg", ".png"])])
        self._build_tab_content(self.tab_frames["🎞️ Video"], [("Level Kompresi:", self.video_level_var, ["Kualitas Tinggi", "Seimbang", "Ekstrem"]), ("Format Output:", self.video_ext_var, [".mp4", ".mkv", ".webm"])])

    def _set_active_tab(self, tab_name):
        self.current_tab_name = tab_name
        
        for name, btn in self.tab_buttons.items():
            if name == tab_name:
                btn.configure(fg_color=self.BTN_SUCCESS, border_color=self.BTN_SUCCESS_BORDER, text_color="white", hover_color=self.BTN_SUCCESS_HOVER)
            else:
                btn.configure(fg_color=self.BG_BASE, border_color=self.BORDER_SUNKEN, text_color="#A9A9A9", hover_color="#333333")
                
        for name, f in self.tab_frames.items():
            f.pack_forget()
        self.tab_frames[tab_name].pack(fill="both", expand=True)
        
        self._on_tab_change()

    def _build_tab_content(self, parent, options):
        wrapper = tk.Frame(parent, bg=self.PANEL_SUNKEN)
        wrapper.pack(expand=True)
        
        for i, (label, var, values) in enumerate(options):
            ctk.CTkLabel(wrapper, text=label, font=ctk.CTkFont(size=14, weight="bold")).grid(row=0, column=i*2, padx=(20, 10), pady=15, sticky="e")
            ctk.CTkOptionMenu(wrapper, variable=var, values=values, font=ctk.CTkFont(size=13), fg_color=self.PANEL_RAISED, button_color=self.BORDER_RAISED, button_hover_color="#555555").grid(row=0, column=i*2+1, padx=(0, 20), pady=15, sticky="w")

    def _build_actions(self):
        self.action_frame = ctk.CTkFrame(self.main_container, fg_color=self.PANEL_RAISED, border_color=self.BORDER_RAISED, border_width=2, corner_radius=12)
        self.action_frame.pack(side="bottom", fill="x", pady=(15, 0))

        self.compress_btn = ctk.CTkButton(self.action_frame, text="🚀 Mulai Proses", font=ctk.CTkFont(size=16, weight="bold"), command=self._start_processing, height=45, fg_color=self.BTN_PRIMARY, border_color=self.BTN_PRIMARY_BORDER, border_width=2, hover_color=self.BTN_PRIMARY_HOVER)
        self.compress_btn.pack(side="left", fill="x", expand=True, padx=(15, 10), pady=15)

        self.cancel_btn = ctk.CTkButton(self.action_frame, text="🛑 Batal (Force)", font=ctk.CTkFont(size=14, weight="bold"), command=self._cancel_processing, height=45, width=140, fg_color=self.BTN_DANGER, border_color=self.BTN_DANGER_BORDER, border_width=2, hover_color=self.BTN_DANGER_HOVER, state="disabled")
        self.cancel_btn.pack(side="right", padx=(0, 15), pady=15)

    def _build_progress_status(self):
        self.status_container = tk.Frame(self.main_container, bg=self.BG_BASE)
        self.status_container.pack(side="bottom", fill="x", pady=10)
        
        self.progress_bar = ctk.CTkProgressBar(self.status_container, height=12, progress_color=self.BTN_PRIMARY, fg_color=self.PANEL_SUNKEN, border_width=1, border_color=self.BORDER_SUNKEN)
        self.progress_bar.pack(side="bottom", fill="x", padx=5)
        self.progress_bar.set(0)

        self.status_label = ctk.CTkLabel(self.status_container, text="Status: Menunggu Instuksi", font=ctk.CTkFont(weight="bold", size=13), text_color="#A9A9A9")
        self.status_label.pack(side="bottom", pady=(0, 8))

    def _build_settings(self):
        self.settings_frame = ctk.CTkFrame(self.main_container, fg_color=self.PANEL_RAISED, border_color=self.BORDER_RAISED, border_width=2, corner_radius=10)
        self.settings_frame.pack(side="bottom", fill="x", pady=(10, 0))
        
        self.settings_frame.grid_columnconfigure(4, weight=1)

        ctk.CTkLabel(self.settings_frame, text="Folder Output:", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=(20, 10), pady=15, sticky="w")
        
        self.out_btn = ctk.CTkButton(self.settings_frame, text="Pilih Folder...", command=self._browse_output_dir, width=120, fg_color="#444444", border_width=1, border_color="#555555", hover_color="#2B2B2B")
        self.out_btn.grid(row=0, column=1, padx=5, pady=15, sticky="w")
        
        self.out_lbl = ctk.CTkLabel(self.settings_frame, text="(Mengikuti folder asal)", text_color="#888888")
        self.out_lbl.grid(row=0, column=2, padx=10, pady=15, sticky="w")
        
        self.info_icon = ctk.CTkLabel(self.settings_frame, text="ℹ", font=ctk.CTkFont(size=16, weight="bold"), cursor="hand2")
        self.info_icon.grid(row=0, column=3, padx=(5, 10), pady=15, sticky="w")
        self.info_icon.bind("<Enter>", self._on_info_enter)
        self.info_icon.bind("<Leave>", self._on_info_leave)

        self.donate_btn = ctk.CTkButton(
            self.settings_frame, text="☕ Traktir Kopi", width=120,
            fg_color="transparent", border_width=1, border_color="#FF9800",
            text_color="#FFB74D", hover_color="#4E342E",
            command=lambda: webbrowser.open("https://saweria.co/Denian00")
        )
        self.donate_btn.grid(row=0, column=4, padx=20, pady=15, sticky="e")

    def _build_dropzone(self):
        self.input_frame = ctk.CTkFrame(self.main_container, corner_radius=15, border_width=3, border_color=self.BORDER_SUNKEN, fg_color=self.PANEL_SUNKEN)
        self.input_frame.pack(side="top", fill="both", expand=True, pady=10)
        self.input_frame.drop_target_register(DND_FILES)
        self.input_frame.dnd_bind("<<Drop>>", self._on_file_drop)

        self.btn_frame = tk.Frame(self.input_frame, bg=self.PANEL_SUNKEN)
        self.btn_frame.pack(side="top", pady=15)
        
        self.btn_file = ctk.CTkButton(self.btn_frame, text="📄 Pilih File", command=self._browse_file, fg_color="#424242", hover_color="#616161", border_width=2, border_color="#757575")
        self.btn_file.pack(side="left", padx=10)
        
        self.btn_folder = ctk.CTkButton(self.btn_frame, text="📁 Pilih Folder (Batch)", command=self._browse_folder, fg_color=self.BTN_SUCCESS, border_color=self.BTN_SUCCESS_BORDER, border_width=2, hover_color=self.BTN_SUCCESS_HOVER)
        self.btn_folder.pack(side="left", padx=10)
        
        self.btn_clear = ctk.CTkButton(self.btn_frame, text="🗑️ Bersihkan", command=self._clear_queue, fg_color="transparent", border_width=1, border_color="#C62828", text_color="#EF9A9A", hover_color="#4A141C")
        self.btn_clear.pack(side="left", padx=10)

        self.lists_container = tk.PanedWindow(self.input_frame, orient="horizontal", bg="#4A4A4A", bd=0, sashwidth=6, sashrelief="flat")
        self.lists_container.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        self.list_wrappers = {}
        self.list_frames = {}
        
        for t in self.tabs_list:
            w_in = tk.Frame(self.lists_container, bg=self.PANEL_SUNKEN)
            w_out = tk.Frame(self.lists_container, bg=self.PANEL_SUNKEN)
            
            f_in = ctk.CTkScrollableFrame(w_in, label_text=f"Daftar Input {t.split()[1]} (Klik untuk Buka)", fg_color=self.LIST_BG, scrollbar_button_color="#333", scrollbar_button_hover_color="#555")
            f_in.pack(fill="both", expand=True, padx=(0, 2))
            
            f_out = ctk.CTkScrollableFrame(w_out, label_text=f"Daftar Output {t.split()[1]} (Selesai)", fg_color=self.LIST_BG, scrollbar_button_color="#333", scrollbar_button_hover_color="#555")
            f_out.pack(fill="both", expand=True, padx=(2, 0))
            
            self.list_wrappers[t] = {"in": w_in, "out": w_out}
            self.list_frames[t] = {"in": f_in, "out": f_out}
            
        self.placeholders = {}
        for t in self.tabs_list:
            lbl = ctk.CTkLabel(self.list_frames[t]["in"], text="Anda bisa drag and drop juga\nuntuk memasukkan file", text_color="#555555", font=ctk.CTkFont(size=14, slant="italic"), justify="center")
            self.placeholders[t] = lbl

    # ==================== First Run & Popup (Redesigned) ====================
    def _check_first_run(self):
        # DIBUAT SELALU TRUE SESUAI INSTRUKSI MODE PENGUJIAN
        is_first = True 
        if is_first:
            self.after(500, self._show_welcome_popup)

    def _show_welcome_popup(self):
        popup = ctk.CTkToplevel(self)
        popup.title("Dukungan Kreator")
        # Diperbesar untuk mengakomodasi padding dan gambar besar
        popup.geometry("560x520")
        popup.attributes("-topmost", True)
        
        try:
            popup.after(200, lambda: popup.iconbitmap(resource_path("assets/logo.ico")))
        except Exception:
            pass
            
        popup.grab_set()
        popup.focus()
        
        self.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - 560) // 2
        y = self.winfo_y() + (self.winfo_height() - 520) // 2
        popup.geometry(f"+{max(0, x)}+{max(0, y)}")
        
        # Tema super minimalis gelap
        popup.configure(fg_color="#1A1A1A")
        
        # 1. Gambar Kucing Hitam (The Noir)
        img_path = resource_path(os.path.join("assets", "the_noir.png"))
        if os.path.exists(img_path):
            try:
                original_img = Image.open(img_path)
                # Jaga aspect ratio agar tidak gepeng
                orig_w, orig_h = original_img.size
                target_w = 150
                ratio = target_w / orig_w
                target_h = int(orig_h * ratio)
                
                cat_img = ctk.CTkImage(light_image=original_img, size=(target_w, target_h))
                lbl_img = ctk.CTkLabel(popup, text="", image=cat_img)
                # pady=(50, 0) agar gambar turun dan menempel rapat dengan teks di bawahnya
                lbl_img.pack(pady=(50, 0))
            except Exception:
                pass
        else:
            # Fallback jika gambar belum ada di folder assets
            placeholder_lbl = ctk.CTkLabel(popup, text="[ Gambar The Noir ]", font=ctk.CTkFont(size=14, slant="italic"), text_color="#555")
            placeholder_lbl.pack(pady=(50, 0))

        # 2. Tata Letak Bersih & Hierarki Teks
        lbl_title = ctk.CTkLabel(popup, text="Terima kasih telah menggunakan\nDenian Media Pro!", font=ctk.CTkFont(size=22, weight="bold"), text_color="#FFFFFF")
        # pady=(0, 15) memastikan jarak 0 dari sisi atas (nempel dengan kaki kucing)
        lbl_title.pack(pady=(0, 15))
        
        # Teks isi lebih rapi dan ringkas
        body_text = ("Dukungan Anda sangat berarti bagi pengembangan aplikasi ini.\n"
                     "Bantu saya mewujudkan pembaruan fitur, perbaikan bug,\n"
                     "serta peluncuran tools gratis lainnya dengan secangkir kopi!")
        lbl_body = ctk.CTkLabel(popup, text=body_text, font=ctk.CTkFont(size=14), text_color="#BBBBBB", justify="center")
        lbl_body.pack(pady=(0, 25))
        
        # 3. Gaya Tombol Membulat (Pill-shaped)
        btn_frame = tk.Frame(popup, bg="#1A1A1A")
        btn_frame.pack(pady=(10, 20))
        
        def on_donate():
            webbrowser.open("https://saweria.co/Denian00")
            popup.destroy()
            
        btn_donate = ctk.CTkButton(
            btn_frame, text="Traktir Kopi ☕", 
            fg_color="#FF9800", hover_color="#F57C00", text_color="white", 
            font=ctk.CTkFont(weight="bold", size=15), 
            height=46, width=160, corner_radius=25, command=on_donate
        )
        btn_donate.pack(side="left", padx=12)
        
        btn_skip = ctk.CTkButton(
            btn_frame, text="Nanti Saja", 
            fg_color="#333333", hover_color="#444444", text_color="#AAAAAA", 
            font=ctk.CTkFont(weight="bold", size=14), 
            height=46, width=120, corner_radius=25, command=popup.destroy
        )
        btn_skip.pack(side="left", padx=12)

        # Catatan P.S di bawah
        ps_text = "P.S. Punya saran atau request fitur? Sampaikan pesan Anda saat traktir kopi ya!"
        lbl_ps = ctk.CTkLabel(popup, text=ps_text, font=ctk.CTkFont(size=12, slant="italic"), text_color="#555555", justify="center")
        lbl_ps.pack(side="bottom", pady=(0, 30))

    # ==================== Interactions ====================

    def _on_info_enter(self, event):
        if not self.is_processing:
            self.prev_status = self.status_label.cget("text")
            self.status_label.configure(text="Rekomendasi: Buat & pilih folder baru untuk menyimpan file hasil kompresi.", text_color="#FFD54F")

    def _on_info_leave(self, event):
        if not self.is_processing:
            self.status_label.configure(text=self.prev_status, text_color="#A9A9A9")

    def _open_file(self, path):
        if os.path.exists(path):
            try:
                if sys.platform == "win32":
                    os.startfile(path)
                elif sys.platform == "darwin":
                    subprocess.call(["open", path])
                else:
                    subprocess.call(["xdg-open", path])
            except Exception as e:
                pass

    def _on_tab_change(self):
        curr_tab = self.current_tab_name
        
        for pane in self.lists_container.panes():
            self.lists_container.remove(pane)
            
        self.lists_container.add(self.list_wrappers[curr_tab]["in"], minsize=200, stretch="always")
        self.lists_container.add(self.list_wrappers[curr_tab]["out"], minsize=200, stretch="always")
        
        self._update_placeholder()

    def _update_placeholder(self):
        curr_tab = self.current_tab_name
        for lbl in self.placeholders.values():
            lbl.pack_forget()
            
        if not self.file_queues[curr_tab]:
            self.placeholders[curr_tab].pack(expand=True, fill="both", pady=50)

    def _get_supported_exts(self, tab):
        if "PDF" in tab: return [".pdf"]
        if "Foto" in tab: return [".jpg", ".jpeg", ".png", ".webp", ".bmp"]
        if "Video" in tab: return [".mp4", ".mkv", ".webm", ".avi", ".mov", ".flv"]
        return []

    def _add_to_queue(self, file_path, update_placeholder=True):
        if not os.path.isfile(file_path): return False
        curr_tab = self.current_tab_name
        exts = self._get_supported_exts(curr_tab)
        if not file_path.lower().endswith(tuple(exts)): return False
        
        for item in self.file_queues[curr_tab]:
            if item["path"] == file_path: return False

        parent_frame = self.list_frames[curr_tab]["in"]
        
        row_frame = tk.Frame(parent_frame, bg=self.LIST_BG)
        row_frame.pack(fill="x", pady=2, padx=5)
        
        var = ctk.BooleanVar(value=True)
        size_str = format_file_size(os.path.getsize(file_path))
        name = os.path.basename(file_path)

        chk = ctk.CTkCheckBox(row_frame, text="", variable=var, width=24, fg_color=self.BTN_PRIMARY)
        chk.pack(side="left", padx=(5, 0))

        lbl_name = ctk.CTkLabel(row_frame, text=f"{name} ({size_str})", cursor="hand2", text_color="#64B5F6", anchor="w")
        lbl_name.pack(side="left", padx=5, fill="x", expand=True)
        lbl_name.bind("<Button-1>", lambda e, p=file_path: self._open_file(p))

        lbl_status = ctk.CTkLabel(row_frame, text="Menunggu", text_color="gray", width=80, anchor="e")
        lbl_status.pack(side="right", padx=5)

        self.file_queues[curr_tab].append({
            "path": file_path,
            "var": var,
            "status_label": lbl_status,
            "frame": row_frame
        })
        
        if update_placeholder:
            self._update_placeholder()
            
        return True

    def _on_file_drop(self, event):
        paths = self.tk.splitlist(event.data)
        for p in paths:
            if os.path.isdir(p): self._scan_folder(p)
            else: self._add_to_queue(p)

    def _browse_file(self):
        paths = filedialog.askopenfilenames(title="Pilih File")
        for p in paths: self._add_to_queue(p)

    def _browse_folder(self):
        folder = filedialog.askdirectory(title="Pilih Folder (Batch)")
        if folder: self._scan_folder(folder)

    def _scan_folder(self, folder):
        added = 0
        try:
            for f in os.listdir(folder):
                full_path = os.path.join(folder, f)
                if os.path.isfile(full_path):
                    if self._add_to_queue(full_path, update_placeholder=False):
                        added += 1
        except Exception as e:
            pass
            
        self._update_placeholder()
        
        if added == 0:
            curr_tab = self.current_tab_name.split()[1]
            messagebox.showinfo("Folder Kosong", f"Tidak ada file {curr_tab} yang didukung di dalam folder tersebut.")

    def _clear_queue(self):
        if self.is_processing: return
        curr_tab = self.current_tab_name
        for item in self.file_queues[curr_tab]:
            item["frame"].destroy()
        self.file_queues[curr_tab].clear()
        
        for child in self.list_frames[curr_tab]["out"].winfo_children():
            child.destroy()
            
        self.status_label.configure(text="Status: Siap", text_color="#A9A9A9")
        self._update_placeholder()

    def _browse_output_dir(self):
        folder = filedialog.askdirectory(title="Folder Output")
        if folder:
            self.output_directory = os.path.abspath(folder)
            self.out_lbl.configure(text=self.output_directory)

    # ==================== Processing Engine ====================

    def _cancel_processing(self):
        if self.is_processing:
            self.is_cancelled = True
            self.status_label.configure(text="Membatalkan... Menunggu proses dihentikan", text_color="#EF9A9A")
            self.cancel_btn.configure(state="disabled")
            if self.current_process:
                try: self.current_process.kill()
                except: pass

    def _start_processing(self):
        if self.is_processing: return
        curr_tab = self.current_tab_name
        active_items = [x for x in self.file_queues[curr_tab] if x["var"].get()]
        if not active_items:
            messagebox.showwarning("Kosong", "Tidak ada file yang dicentang.")
            return

        self.is_processing = True
        self.is_cancelled = False
        self.compress_btn.configure(state="disabled", text="⏳ Sedang Memproses...")
        self.cancel_btn.configure(state="normal")
        self.progress_bar.set(0)

        for item in self.file_queues[curr_tab]:
            if item["var"].get():
                item["status_label"].configure(text="Menunggu", text_color="gray")

        worker = threading.Thread(target=self._process_queue_thread, args=(active_items, curr_tab), daemon=True)
        worker.start()

    def _add_to_output_list(self, file_path, orig_size, new_size, tab):
        parent = self.list_frames[tab]["out"]
        
        row_frame = tk.Frame(parent, bg=self.LIST_BG)
        row_frame.pack(fill="x", pady=2, padx=5)
        
        name = os.path.basename(file_path)
        pct = ((orig_size - new_size) / orig_size * 100) if orig_size > 0 else 0
        size_str = format_file_size(new_size)
        
        txt = f"✅ {name} ({size_str}) - Hemat {pct:.1f}%" if pct > 0 else f"✅ {name} ({size_str}) - Optimal"
        lbl_name = ctk.CTkLabel(row_frame, text=txt, cursor="hand2", text_color="#81C784", anchor="w")
        lbl_name.pack(side="left", padx=10, fill="x", expand=True)
        lbl_name.bind("<Button-1>", lambda e, p=file_path: self._open_file(p))

    def _add_to_output_list_skipped(self, file_path, tab):
        parent = self.list_frames[tab]["out"]
        row_frame = tk.Frame(parent, bg=self.LIST_BG)
        row_frame.pack(fill="x", pady=2, padx=5)
        
        name = os.path.basename(file_path)
        lbl_name = ctk.CTkLabel(row_frame, text=f"⏭️ {name} (Sudah Ada)", cursor="hand2", text_color="#FFD54F", anchor="w")
        lbl_name.pack(side="left", padx=10, fill="x", expand=True)
        lbl_name.bind("<Button-1>", lambda e, p=file_path: self._open_file(p))

    def _set_indeterminate(self, enable):
        if enable:
            self.progress_bar.configure(mode="indeterminate")
            self.progress_bar.start()
        else:
            self.progress_bar.stop()
            self.progress_bar.configure(mode="determinate")
            self.progress_bar.set(0)

    def _update_video_progress(self, pct, item, idx, total, name):
        self.progress_bar.set(pct)
        pct_str = f"{int(pct * 100)}%"
        self.status_label.configure(text=f"Status: Memproses {name}... ({pct_str}) [File {idx+1}/{total}]", text_color="#4FC3F7")
        item["status_label"].configure(text=f"Memproses {pct_str}", text_color="#4FC3F7")

    def _process_queue_thread(self, active_items, tab):
        total = len(active_items)
        success_count = 0
        skipped_count = 0
        
        for idx, item in enumerate(active_items):
            if self.is_cancelled:
                self.after(0, item["status_label"].configure, {"text": "Dibatalkan", "text_color": "#EF9A9A"})
                continue

            in_path = item["path"]
            base_name = os.path.splitext(os.path.basename(in_path))[0]
            name_ext = os.path.basename(in_path)
            
            out_dir = self.output_directory or os.path.dirname(in_path)
            os.makedirs(out_dir, exist_ok=True)
            
            # Determine output extension & path
            if "PDF" in tab:
                out_path = os.path.join(out_dir, f"{base_name}_comp.pdf")
            elif "Foto" in tab:
                ext = self.foto_ext_var.get()
                out_path = os.path.join(out_dir, f"{base_name}_comp{ext}")
            else:
                ext = self.video_ext_var.get()
                out_path = os.path.join(out_dir, f"{base_name}_comp{ext}")

            # 1. Skip Existing File Check
            if os.path.exists(out_path):
                self.after(0, item["status_label"].configure, {"text": "Sudah Ada", "text_color": "#FFD54F"})
                self.after(0, self.status_label.configure, {"text": f"File {name_ext} sudah ada, melewati...", "text_color": "#FFD54F"})
                self.after(0, self._add_to_output_list_skipped, out_path, tab)
                skipped_count += 1
                continue

            success = False
            err_msg = ""

            try:
                if "PDF" in tab or "Foto" in tab:
                    self.after(0, self._set_indeterminate, True)
                    self.after(0, item["status_label"].configure, {"text": "Memproses", "text_color": "#4FC3F7"})
                    self.after(0, self.status_label.configure, {"text": f"Status: Memproses PDF/Foto {name_ext}... Harap tunggu.", "text_color": "#4FC3F7"})
                    
                    if "PDF" in tab:
                        mode = self.pdf_mode_var.get()
                        success, err_msg = self._run_pdf(in_path, out_path, mode)
                    else:
                        lvl = self.foto_level_var.get()
                        success, err_msg = self._run_ffmpeg_photo(in_path, out_path, lvl, ext)
                        
                    self.after(0, self._set_indeterminate, False)

                elif "Video" in tab:
                    self.after(0, self.progress_bar.configure, {"mode": "determinate"})
                    self.after(0, self.progress_bar.set, 0)
                    lvl = self.video_level_var.get()
                    success, err_msg = self._run_ffmpeg_video_progress(in_path, out_path, lvl, ext, item, idx, total, name_ext)

            except Exception as e:
                success = False
                err_msg = str(e)

            if success and not self.is_cancelled:
                success_count += 1
                orig = os.path.getsize(in_path)
                new = os.path.getsize(out_path) if os.path.exists(out_path) else orig
                self.after(0, item["status_label"].configure, {"text": "Selesai", "text_color": "#81C784"})
                self.after(0, self._add_to_output_list, out_path, orig, new, tab)
            else:
                if os.path.exists(out_path):
                    try: os.remove(out_path)
                    except: pass
                
                if self.is_cancelled:
                    self.after(0, item["status_label"].configure, {"text": "Dibatalkan", "text_color": "#EF9A9A"})
                else:
                    self.after(0, item["status_label"].configure, {"text": "Gagal", "text_color": "#EF9A9A"})
                    print(f"Error on {name_ext}: {err_msg}")
            
            self.after(0, self.progress_bar.set, 1.0)

        self.after(0, self._on_queue_finished, total, success_count, skipped_count)

    def _on_queue_finished(self, total, success_count, skipped_count):
        self.is_processing = False
        self.progress_bar.stop()
        self.progress_bar.configure(mode="determinate")
        self.progress_bar.set(1.0)
        self.compress_btn.configure(state="normal", text="🚀 Mulai Proses")
        self.cancel_btn.configure(state="disabled")

        if self.is_cancelled:
            self.status_label.configure(text=f"Dihentikan. Berhasil: {success_count}, Dilewati: {skipped_count}, Total: {total}", text_color="#EF9A9A")
            messagebox.showwarning("Dibatalkan", f"Proses dihentikan massal.\nFile sukses: {success_count}\nDilewati: {skipped_count}")
        else:
            self.status_label.configure(text=f"Selesai! Berhasil memproses {success_count} file. ({skipped_count} dilewati)", text_color="#81C784")
            messagebox.showinfo("Selesai", f"Pemrosesan massal selesai!\nBerhasil: {success_count}\nDilewati (Sudah Ada): {skipped_count}\nGagal: {total - success_count - skipped_count}")

    # ==================== Subprocess Execution Methods ====================

    def _exec_cmd(self, cmd, out_path):
        startupinfo = None
        creationflags = 0
        if sys.platform == "win32":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = 0
            creationflags = subprocess.CREATE_NO_WINDOW

        self.current_process = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
            startupinfo=startupinfo, creationflags=creationflags
        )
        out, err = self.current_process.communicate()
        self.current_process = None

        if self.is_cancelled:
            return False, "Cancelled"

        if os.path.exists(out_path) and os.path.getsize(out_path) > 0:
            return True, ""
            
        return False, f"Exit code error. {err}"

    def _run_pdf(self, input_path, output_path, mode):
        if "Aman" in mode:
            exe = resource_path(os.path.join("assets", "qpdf.exe"))
            cmd = [exe, "--linearize", "--optimize-images", input_path, output_path]
        else:
            exe = resource_path(os.path.join("assets", "gswin64c.exe"))
            cmd = [exe, "-sDEVICE=pdfwrite", "-dCompatibilityLevel=1.4", "-dPDFSETTINGS=/ebook", "-dNOPAUSE", "-dQUIET", "-dBATCH", f"-sOutputFile={output_path}", input_path]
        return self._exec_cmd(cmd, output_path)

    def _run_ffmpeg_photo(self, input_path, output_path, level, ext):
        exe = resource_path(os.path.join("assets", "ffmpeg.exe"))
        cmd = [exe, "-y", "-i", input_path]
        if ext == ".webp":
            if level == "Kualitas Tinggi": cmd.extend(["-c:v", "libwebp", "-q:v", "80"])
            elif level == "Seimbang": cmd.extend(["-c:v", "libwebp", "-q:v", "50"])
            else: cmd.extend(["-c:v", "libwebp", "-q:v", "20", "-vf", r"scale='w=min(1280\,iw):h=-2'"])
        elif ext == ".jpg":
            if level == "Kualitas Tinggi": cmd.extend(["-q:v", "2"])
            elif level == "Seimbang": cmd.extend(["-q:v", "6"])
            else: cmd.extend(["-q:v", "12", "-vf", r"scale='w=min(1280\,iw):h=-2'"])
        else: # .png
            cmd.extend(["-compression_level", "9"])
            if level == "Ekstrem": cmd.extend(["-vf", r"scale='w=min(1280\,iw):h=-2'"])
        cmd.append(output_path)
        return self._exec_cmd(cmd, output_path)

    def _run_ffmpeg_video_progress(self, input_path, output_path, level, ext, item, idx, total, name_ext):
        exe = resource_path(os.path.join("assets", "ffmpeg.exe"))
        cmd = [exe, "-y", "-i", input_path]
        vcodec = "libx264"
        if ext == ".webm": vcodec = "libvpx-vp9"
        cmd.extend(["-c:v", vcodec])

        if level == "Kualitas Tinggi":
            cmd.extend(["-crf", "23", "-preset", "medium" if ext != ".webm" else "good", "-c:a", "aac", "-b:a", "192k"])
        elif level == "Seimbang":
            cmd.extend(["-crf", "28", "-preset", "fast" if ext != ".webm" else "good", "-c:a", "aac", "-b:a", "128k"])
        else:
            cmd.extend(["-crf", "35", "-preset", "veryfast" if ext != ".webm" else "good", "-vf", r"scale='w=min(1280\,iw):h=-2'", "-c:a", "aac", "-b:a", "96k"])
        cmd.append(output_path)

        startupinfo = None
        creationflags = 0
        if sys.platform == "win32":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = 0
            creationflags = subprocess.CREATE_NO_WINDOW

        self.current_process = subprocess.Popen(
            cmd, stderr=subprocess.PIPE, text=True, bufsize=1, universal_newlines=True,
            startupinfo=startupinfo, creationflags=creationflags
        )
        
        duration_sec = 0.0
        time_pattern = re.compile(r"time=(\d{2}):(\d{2}):(\d{2}\.\d{2})")
        duration_pattern = re.compile(r"Duration: (\d{2}):(\d{2}):(\d{2}\.\d{2})")
        
        for line in self.current_process.stderr:
            if self.is_cancelled:
                self.current_process.kill()
                break
                
            if duration_sec == 0.0:
                dur_match = duration_pattern.search(line)
                if dur_match:
                    h, m, s = dur_match.groups()
                    duration_sec = int(h)*3600 + int(m)*60 + float(s)
            
            time_match = time_pattern.search(line)
            if time_match and duration_sec > 0:
                h, m, s = time_match.groups()
                curr_time = int(h)*3600 + int(m)*60 + float(s)
                pct = min(curr_time / duration_sec, 1.0)
                self.after(0, self._update_video_progress, pct, item, idx, total, name_ext)
                
        self.current_process.wait()
        success = (self.current_process.returncode == 0) and not self.is_cancelled
        self.current_process = None
        
        if success and os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            return True, ""
        return False, "Failed or Cancelled"

def main():
    app = DenianMediaProApp()
    app.mainloop()

if __name__ == "__main__":
    main()

"""
PDF Compressor Application (GUI)
A bulletproof desktop wrapper for QPDF and Ghostscript compression engines.
Built with CustomTkinter and TkinterDnD2.
Features: PyInstaller Ready, Async Subprocess, Force Stop, Auto Cleanup & Bilingual Support.
"""

import os
import sys
import threading
import subprocess
from tkinter import filedialog, messagebox
import customtkinter as ctk
from tkinterdnd2 import TkinterDnD, DND_FILES

TRANSLATIONS = {
    "ID": {
        "title": "Denian pdf Pro",
        "subtitle": "Kompres dokumen PDF secara cepat, aman, dan efisien",
        "drop_main": "Tarik & Letakkan (Drag & Drop) File PDF di Sini",
        "drop_sub": "atau klik tombol di bawah untuk memilih file manual",
        "btn_browse": "Pilih File PDF",
        "no_file": "Belum ada file yang dipilih",
        "mode_label": "Mode Kompresi:",
        "mode_safe": "Aman (Tanpa Blur / Lossless)",
        "mode_ext": "Ekstrem (Ukuran Terkecil)",
        "out_label": "Folder Output:",
        "btn_out": "Pilih Folder...",
        "out_display_default": "Folder Output: (Mengikuti folder asal file)",
        "status_ready": "Status: Siap",
        "btn_compress": "🚀 Mulai Kompresi PDF",
        "btn_compressing": "⏳ Sedang Mengompres...",
        "btn_cancel": "🛑 Batal",
        "btn_open": "📁 Buka File Hasil",
        "status_file_ready": "Status: File siap dikompres",
        "status_compressing": "Status: Memproses kompresi...",
        "status_cancelling": "Status: Membatalkan proses...",
        "status_cancelled": "Status: Proses Dibatalkan oleh Pengguna!",
        "status_failed": "Status: Kompresi Gagal",
        "msg_file_not_found": "File tidak valid atau tidak ditemukan.",
        "msg_unsupported": "Harap pilih dokumen berekstensi .pdf",
        "msg_select_first": "Pilih file PDF terlebih dahulu!",
        "msg_locked": "File sedang dibuka di aplikasi lain.\nSilakan tutup terlebih dahulu.",
        "msg_cancel_warn": "Proses kompresi telah dihentikan.\nFile sementara yang belum jadi telah dihapus.",
        "msg_success": "Proses kompresi berhasil!",
        "msg_optimal": "Ukuran file sudah paling optimal",
        "lbl_selected": "Terpilih",
        "lbl_loc": "Lokasi",
        "success_title": "Selesai",
        "failed_title": "Gagal Memproses",
        "locked_title": "File Terkunci",
        "warn_title": "Peringatan",
        "info_original": "Ukuran Awal",
        "info_new": "Ukuran Baru",
        "info_saved": "Disimpan di",
        "hemat": "Hemat"
    },
    "EN": {
        "title": "Denian pdf Pro",
        "subtitle": "Compress PDF documents quickly, safely, and efficiently",
        "drop_main": "Drag & Drop PDF File Here",
        "drop_sub": "or click the button below to select manually",
        "btn_browse": "Select PDF File",
        "no_file": "No file selected",
        "mode_label": "Compression Mode:",
        "mode_safe": "Safe (No Blur / Lossless)",
        "mode_ext": "Extreme (Smallest Size)",
        "out_label": "Output Folder:",
        "btn_out": "Browse...",
        "out_display_default": "Output Folder: (Same as source file)",
        "status_ready": "Status: Ready",
        "btn_compress": "🚀 Start Compression",
        "btn_compressing": "⏳ Compressing...",
        "btn_cancel": "🛑 Cancel",
        "btn_open": "📁 Open Output",
        "status_file_ready": "Status: File ready to compress",
        "status_compressing": "Status: Processing compression...",
        "status_cancelling": "Status: Cancelling process...",
        "status_cancelled": "Status: Process Cancelled by User!",
        "status_failed": "Status: Compression Failed",
        "msg_file_not_found": "File is invalid or not found.",
        "msg_unsupported": "Please select a .pdf document.",
        "msg_select_first": "Please select a PDF file first!",
        "msg_locked": "File is being used by another app.\nPlease close it first.",
        "msg_cancel_warn": "Compression has been stopped.\nIncomplete temporary files have been removed.",
        "msg_success": "Compression successful!",
        "msg_optimal": "File size is already optimal",
        "lbl_selected": "Selected",
        "lbl_loc": "Location",
        "success_title": "Completed",
        "failed_title": "Processing Failed",
        "locked_title": "File Locked",
        "warn_title": "Warning",
        "info_original": "Original Size",
        "info_new": "New Size",
        "info_saved": "Saved at",
        "hemat": "Saved"
    }
}


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


class PDFCompressorApp(ctk.CTk, TkinterDnD.DnDWrapper):
    def __init__(self):
        super().__init__()
        self.TkdndVersion = TkinterDnD._require(self)

        # State Variables
        self.current_lang = "ID"
        self.input_file_path: str = ""
        self.output_directory: str = ""
        self.is_compressing: bool = False
        self.is_cancelled: bool = False
        self.last_output_file: str = ""
        self.current_process: subprocess.Popen = None

        # Window Config
        self.title("Denian pdf Pro")
        try:
            self.iconbitmap(resource_path("assets/logo.ico"))
        except:
            pass
        self.geometry("660x720")
        self.minsize(600, 680)

        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")

        self._build_ui()
        self._update_ui_texts()

    def get_t(self, key):
        return TRANSLATIONS[self.current_lang][key]

    def _build_ui(self):
        self.main_container = ctk.CTkFrame(self, corner_radius=12)
        self.main_container.pack(fill="both", expand=True, padx=20, pady=20)

        # Language Switcher
        self.header_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.header_frame.pack(fill="x", pady=(10, 0), padx=20)
        
        self.lang_option = ctk.CTkOptionMenu(
            self.header_frame, 
            values=["🇮🇩 ID", "🇬🇧 EN"], 
            command=self._change_language,
            width=80,
            height=28
        )
        self.lang_option.pack(side="right")

        # 1. Header
        self.header_title = ctk.CTkLabel(
            self.main_container,
            text="Denian pdf Pro",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.header_title.pack(pady=(0, 4))

        self.header_subtitle = ctk.CTkLabel(
            self.main_container,
            text="",
            font=ctk.CTkFont(size=13),
            text_color="gray"
        )
        self.header_subtitle.pack(pady=(0, 16))

        # 2. Dropzone
        self.drop_frame = ctk.CTkFrame(
            self.main_container,
            corner_radius=10,
            border_width=2,
            border_color="#3B8ED0",
            fg_color=("gray85", "#1E1E24")
        )
        self.drop_frame.pack(fill="x", padx=24, pady=8, ipady=20)

        self.drop_frame.drop_target_register(DND_FILES)
        self.drop_frame.dnd_bind("<<Drop>>", self._on_file_drop)

        self.drop_icon_label = ctk.CTkLabel(self.drop_frame, text="📄", font=ctk.CTkFont(size=36))
        self.drop_icon_label.pack(pady=(8, 2))

        self.drop_text_main = ctk.CTkLabel(self.drop_frame, text="", font=ctk.CTkFont(size=14, weight="bold"))
        self.drop_text_main.pack(pady=(2, 2))

        self.drop_text_sub = ctk.CTkLabel(self.drop_frame, text="", font=ctk.CTkFont(size=12), text_color="gray")
        self.drop_text_sub.pack(pady=(0, 8))

        self.browse_file_btn = ctk.CTkButton(self.drop_frame, text="", command=self._browse_input_file, width=150, height=32)
        self.browse_file_btn.pack(pady=(2, 6))

        self.file_info_frame = ctk.CTkFrame(self.drop_frame, fg_color="transparent")
        self.file_info_frame.pack(fill="x", padx=16, pady=(4, 0))

        self.selected_file_label = ctk.CTkLabel(
            self.file_info_frame,
            text="",
            font=ctk.CTkFont(size=12, slant="italic"),
            text_color="#9E9E9E",
            wraplength=500
        )
        self.selected_file_label.pack()

        # 3. Settings
        self.settings_frame = ctk.CTkFrame(self.main_container, corner_radius=8)
        self.settings_frame.pack(fill="x", padx=24, pady=12)

        self.mode_label = ctk.CTkLabel(self.settings_frame, text="", font=ctk.CTkFont(size=13, weight="bold"))
        self.mode_label.grid(row=0, column=0, padx=(16, 8), pady=12, sticky="w")

        self.mode_option = ctk.CTkOptionMenu(self.settings_frame, values=["1", "2"], width=280)
        self.mode_option.grid(row=0, column=1, padx=(0, 16), pady=12, sticky="ew")

        self.output_label = ctk.CTkLabel(self.settings_frame, text="", font=ctk.CTkFont(size=13, weight="bold"))
        self.output_label.grid(row=1, column=0, padx=(16, 8), pady=(0, 12), sticky="w")

        self.output_browse_btn = ctk.CTkButton(self.settings_frame, text="", command=self._browse_output_dir, width=120, height=30)
        self.output_browse_btn.grid(row=1, column=1, padx=(0, 16), pady=(0, 12), sticky="w")

        self.output_path_display = ctk.CTkLabel(
            self.settings_frame,
            text="",
            font=ctk.CTkFont(size=11),
            text_color="gray",
            anchor="w",
            wraplength=480
        )
        self.output_path_display.grid(row=2, column=0, columnspan=2, padx=16, pady=(0, 12), sticky="w")
        self.settings_frame.columnconfigure(1, weight=1)

        # 4. Progress & Status
        self.progress_bar = ctk.CTkProgressBar(self.main_container)
        self.progress_bar.pack(fill="x", padx=24, pady=(6, 4))
        self.progress_bar.set(0)

        self.status_label = ctk.CTkLabel(self.main_container, text="", font=ctk.CTkFont(size=12, weight="bold"), text_color="#3B8ED0")
        self.status_label.pack(pady=4)

        # 5. Actions
        self.action_btn_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.action_btn_frame.pack(fill="x", padx=24, pady=(10, 8))

        self.compress_btn = ctk.CTkButton(
            self.action_btn_frame,
            text="", font=ctk.CTkFont(size=14, weight="bold"),
            command=self._start_compression_thread,
            height=40, fg_color="#1f6aa5", hover_color="#144870"
        )
        self.compress_btn.pack(side="left", fill="x", expand=True, padx=(0, 6))

        self.cancel_btn = ctk.CTkButton(
            self.action_btn_frame,
            text="", font=ctk.CTkFont(size=14, weight="bold"),
            command=self._cancel_compression,
            height=40, fg_color="#D32F2F", hover_color="#B71C1C",
            state="disabled", width=100
        )
        self.cancel_btn.pack(side="left", padx=(0, 6))

        self.open_output_btn = ctk.CTkButton(
            self.action_btn_frame,
            text="", font=ctk.CTkFont(size=13),
            command=self._open_output_location,
            height=40, state="disabled", width=140
        )
        self.open_output_btn.pack(side="right")

    def _change_language(self, choice):
        self.current_lang = choice.split(" ")[1] # Extracts "ID" or "EN"
        
        # Simpan nilai mode saat ini berdasarkan indeks
        current_mode_val = self.mode_option.get()
        is_safe = (current_mode_val == TRANSLATIONS["ID"]["mode_safe"] or current_mode_val == TRANSLATIONS["EN"]["mode_safe"])
        
        self._update_ui_texts()
        
        # Pulihkan nilai dropdown berdasarkan bahasa baru
        if is_safe:
            self.mode_option.set(self.get_t("mode_safe"))
        else:
            self.mode_option.set(self.get_t("mode_ext"))

    def _update_ui_texts(self):
        """Update all text in UI based on current language."""
        self.header_title.configure(text=self.get_t("title"))
        self.header_subtitle.configure(text=self.get_t("subtitle"))
        self.drop_text_main.configure(text=self.get_t("drop_main"))
        self.drop_text_sub.configure(text=self.get_t("drop_sub"))
        self.browse_file_btn.configure(text=self.get_t("btn_browse"))
        
        if not self.input_file_path:
            self.selected_file_label.configure(text=self.get_t("no_file"))
        else:
            self._update_selected_file_label()

        self.mode_label.configure(text=self.get_t("mode_label"))
        self.mode_option.configure(values=[self.get_t("mode_safe"), self.get_t("mode_ext")])
        
        self.output_label.configure(text=self.get_t("out_label"))
        self.output_browse_btn.configure(text=self.get_t("btn_out"))
        
        if not self.output_directory:
            if self.input_file_path:
                default_dir = os.path.dirname(self.input_file_path)
                self.output_path_display.configure(text=f"{self.get_t('out_label')} {default_dir} (Default)")
            else:
                self.output_path_display.configure(text=self.get_t("out_display_default"))
        else:
            self.output_path_display.configure(text=f"{self.get_t('out_label')} {self.output_directory}")

        if not self.is_compressing:
            self.compress_btn.configure(text=self.get_t("btn_compress"))
            if not self.input_file_path:
                self.status_label.configure(text=self.get_t("status_ready"))
            else:
                self.status_label.configure(text=self.get_t("status_file_ready"))
        else:
            self.compress_btn.configure(text=self.get_t("btn_compressing"))
            if self.is_cancelled:
                self.status_label.configure(text=self.get_t("status_cancelling"))
            else:
                self.status_label.configure(text=self.get_t("status_compressing"))

        self.cancel_btn.configure(text=self.get_t("btn_cancel"))
        self.open_output_btn.configure(text=self.get_t("btn_open"))

    def _update_selected_file_label(self):
        file_size = os.path.getsize(self.input_file_path)
        file_name = os.path.basename(self.input_file_path)
        self.selected_file_label.configure(
            text=f"{self.get_t('lbl_selected')}: {file_name} ({format_file_size(file_size)})\n{self.get_t('lbl_loc')}: {self.input_file_path}"
        )

    # ==================== Core Logic ====================

    def _on_file_drop(self, event):
        paths = self.tk.splitlist(event.data)
        if paths:
            self._set_input_file(paths[0])

    def _browse_input_file(self):
        path = filedialog.askopenfilename(
            title=self.get_t("btn_browse"),
            filetypes=[("PDF Files", "*.pdf"), ("All Files", "*.*")]
        )
        if path:
            self._set_input_file(path)

    def _browse_output_dir(self):
        chosen_dir = filedialog.askdirectory(title=self.get_t("btn_out"))
        if chosen_dir:
            self.output_directory = os.path.abspath(chosen_dir)
            self.output_path_display.configure(
                text=f"{self.get_t('out_label')} {self.output_directory}",
                text_color="#E0E0E0"
            )

    def _set_input_file(self, file_path: str):
        if not file_path or not os.path.exists(file_path):
            messagebox.showwarning(self.get_t("warn_title"), self.get_t("msg_file_not_found"))
            return

        if not file_path.lower().endswith(".pdf"):
            messagebox.showwarning(self.get_t("warn_title"), self.get_t("msg_unsupported"))
            return

        self.input_file_path = os.path.abspath(file_path)
        self._update_selected_file_label()
        self.selected_file_label.configure(text_color="#64B5F6")

        if not self.output_directory:
            default_dir = os.path.dirname(self.input_file_path)
            self.output_path_display.configure(
                text=f"{self.get_t('out_label')} {default_dir} (Default)",
                text_color="gray"
            )

        self.status_label.configure(text=self.get_t("status_file_ready"), text_color="#3B8ED0")
        self.progress_bar.set(0)

    def _cancel_compression(self):
        """Memaksa penghentian kompresi yang sedang berjalan (Force Stop)."""
        if self.is_compressing and self.current_process:
            self.is_cancelled = True
            self.status_label.configure(text=self.get_t("status_cancelling"), text_color="#EF5350")
            self.cancel_btn.configure(state="disabled")
            try:
                self.current_process.kill()
            except Exception as e:
                print(f"Failed to kill process: {e}")

    def _start_compression_thread(self):
        if self.is_compressing:
            return

        if not self.input_file_path or not os.path.exists(self.input_file_path):
            messagebox.showwarning(self.get_t("warn_title"), self.get_t("msg_select_first"))
            return

        out_dir = self.output_directory or os.path.dirname(self.input_file_path)
        try:
            os.makedirs(out_dir, exist_ok=True)
        except OSError as err:
            messagebox.showerror(self.get_t("failed_title"), f"Error:\n{err}")
            return

        base_name, ext = os.path.splitext(os.path.basename(self.input_file_path))
        mode = self.mode_option.get()
        is_safe = (mode == self.get_t("mode_safe") or mode == TRANSLATIONS["ID"]["mode_safe"])
        suffix = "_lossless" if is_safe else "_compressed"
        output_file_path = os.path.join(out_dir, f"{base_name}{suffix}{ext}")

        if os.path.exists(output_file_path):
            try:
                with open(output_file_path, 'a'): 
                    pass
            except OSError:
                messagebox.showerror(self.get_t("locked_title"), self.get_t("msg_locked"))
                return

        self.is_cancelled = False
        self._lock_ui()
        self.status_label.configure(text=self.get_t("status_compressing"), text_color="#FFB74D")
        self.progress_bar.start()

        worker = threading.Thread(
            target=self._run_compression_task,
            args=(self.input_file_path, output_file_path, is_safe),
            daemon=True
        )
        worker.start()

    def _run_compression_task(self, input_path: str, output_path: str, is_safe: bool):
        success = False
        error_message = ""
        startupinfo = None
        creationflags = 0
        if sys.platform == "win32":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = 0 
            creationflags = subprocess.CREATE_NO_WINDOW

        try:
            if is_safe:
                exe_path = resource_path(os.path.join("assets", "qpdf.exe"))
                if not os.path.exists(exe_path):
                    raise FileNotFoundError(f"Missing qpdf.exe")
                cmd = [exe_path, "--linearize", "--optimize-images", input_path, output_path]
            else:
                exe_path = resource_path(os.path.join("assets", "gswin64c.exe"))
                if not os.path.exists(exe_path):
                    raise FileNotFoundError(f"Missing gswin64c.exe")
                cmd = [
                    exe_path, "-sDEVICE=pdfwrite", "-dCompatibilityLevel=1.4",
                    "-dPDFSETTINGS=/ebook", "-dNOPAUSE", "-dQUIET", "-dBATCH",
                    f"-sOutputFile={output_path}", input_path
                ]

            process = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                text=True, startupinfo=startupinfo, creationflags=creationflags
            )
            self.current_process = process
            out, err = process.communicate()

            if self.is_cancelled:
                error_message = "Cancelled"
                success = False
            elif process.returncode == 0 and os.path.exists(output_path):
                success = True
            else:
                out_txt = out.strip() if out else ""
                err_txt = err.strip() if err else ""
                error_message = f"Exit code {process.returncode}:\n{err_txt if err_txt else out_txt}"

        except Exception as exc:
            error_message = f"Exception: {str(exc)}"
        finally:
            self.current_process = None

        self.after(0, self._on_compression_completed, success, input_path, output_path, error_message)

    def _on_compression_completed(self, success: bool, input_path: str, output_path: str, error_message: str):
        self._unlock_ui()
        self.progress_bar.stop()

        if success and os.path.exists(output_path):
            self.progress_bar.set(1.0)
            self.last_output_file = output_path
            self.open_output_btn.configure(state="normal")

            orig_size = os.path.getsize(input_path)
            new_size = os.path.getsize(output_path)
            savings = orig_size - new_size
            pct = (savings / orig_size * 100) if orig_size > 0 else 0

            if savings > 0:
                msg = f"{self.get_t('msg_success')} {format_file_size(orig_size)} ➜ {format_file_size(new_size)} ({self.get_t('hemat')} {pct:.1f}%)"
                self.status_label.configure(text=msg, text_color="#4CAF50")
            else:
                msg = f"{self.get_t('msg_optimal')} ({format_file_size(new_size)})"
                self.status_label.configure(text=msg, text_color="#81C784")

            messagebox.showinfo(
                self.get_t("success_title"),
                f"{self.get_t('msg_success')}\n\n"
                f"{self.get_t('info_original')}: {format_file_size(orig_size)}\n"
                f"{self.get_t('info_new')}: {format_file_size(new_size)}\n\n"
                f"{self.get_t('info_saved')}:\n{output_path}"
            )
        else:
            self.progress_bar.set(0)
            if os.path.exists(output_path):
                try: os.remove(output_path)
                except OSError: pass

            if self.is_cancelled:
                self.status_label.configure(text=self.get_t("status_cancelled"), text_color="#EF5350")
                messagebox.showwarning(self.get_t("warn_title"), self.get_t("msg_cancel_warn"))
            else:
                self.status_label.configure(text=self.get_t("status_failed"), text_color="#E57373")
                messagebox.showerror(self.get_t("failed_title"), f"{error_message}")

    def _open_output_location(self):
        if self.last_output_file and os.path.exists(self.last_output_file):
            if sys.platform == "win32":
                subprocess.run(["explorer", "/select,", os.path.normpath(self.last_output_file)])
            else:
                folder = os.path.dirname(self.last_output_file)
                os.system(f'open "{folder}"' if sys.platform == "darwin" else f'xdg-open "{folder}"')

    def _lock_ui(self):
        self.is_compressing = True
        self.lang_option.configure(state="disabled")
        self.compress_btn.configure(state="disabled", text=self.get_t("btn_compressing"))
        self.cancel_btn.configure(state="normal")
        self.browse_file_btn.configure(state="disabled")
        self.output_browse_btn.configure(state="disabled")
        self.mode_option.configure(state="disabled")
        self.open_output_btn.configure(state="disabled")
        self.drop_frame.drop_target_unregister()

    def _unlock_ui(self):
        self.is_compressing = False
        self.lang_option.configure(state="normal")
        self.compress_btn.configure(state="normal", text=self.get_t("btn_compress"))
        self.cancel_btn.configure(state="disabled")
        self.browse_file_btn.configure(state="normal")
        self.output_browse_btn.configure(state="normal")
        self.mode_option.configure(state="normal")
        self.drop_frame.drop_target_register(DND_FILES)

def main():
    app = PDFCompressorApp()
    app.mainloop()

if __name__ == "__main__":
    main()

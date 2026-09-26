# Blueprint Proyek: GUI Kompresor PDF (Python)

## 1. Deskripsi Proyek
Membuat aplikasi GUI desktop (Windows) berbasis Python yang berfungsi sebagai *wrapper* untuk dua alat CLI kompresi PDF: **QPDF** dan **Ghostscript**. Aplikasi harus mendukung *drag-and-drop* file, pemilihan lokasi penyimpanan (output), dan dibungkus menjadi satu file `.exe` mandiri.

## 2. Struktur Direktori Aktual
Struktur proyek saat ini sudah disiapkan sebagai berikut:

Proyek_Kompresi_GUI/
│
├── assets/                  (Folder berisi semua file mesin kompresi)
│   ├── concrt140.dll
│   ├── fix-qdf.exe
│   ├── msvcp140.dll
│   ├── msvcp140_1.dll
│   ├── msvcp140_2.dll
│   ├── msvcp140_atomic_wait.dll
│   ├── msvcp140_codecvt_ids.dll
│   ├── qpdf.exe             (Eksekusi Utama QPDF)
│   ├── qpdf30.dll
│   ├── vcruntime140.dll
│   ├── vcruntime140_1.dll
│   ├── zlib-flate.exe
│   ├── gsdll64.dll          
│   ├── gsdll64.lib
│   ├── gswin64.exe
│   └── gswin64c.exe         (Eksekusi Utama Ghostscript)
│
└── main.py                  (Script GUI Python utama yang harus dibuat)

## 3. Teknologi yang Digunakan
*   **Bahasa:** Python 3.x
*   **GUI Framework:** `customtkinter` (untuk antarmuka modern)
*   **Drag & Drop:** `tkinterdnd2` (untuk menerima input file PDF)
*   **CLI Execution:** Modul bawaan `subprocess` (menjalankan `.exe` di folder `assets`)
*   **Compiler:** `pyinstaller` (untuk membungkus menjadi `.exe` tunggal)

## 4. Spesifikasi Antarmuka (UI)
Buat jendela `customtkinter` dengan elemen berikut:
1.  **Dropzone (Area Drag & Drop):** Sebuah frame besar di tengah aplikasi. Jika pengguna menyeret file PDF ke area ini, tangkap path absolut file tersebut.
2.  **Opsi Mode Kompresi (Dropdown / OptionMenu):**
    *   `Aman (Tanpa Blur / Lossless)` -> Mode ini akan menggunakan `qpdf.exe`
    *   `Ekstrem (Ukuran Terkecil)` -> Mode ini akan menggunakan `gswin64c.exe`
3.  **Lokasi Output (Tombol & Label):** Tombol "Pilih Folder Output" (`filedialog.askdirectory`) dan label untuk menampilkan path folder yang dipilih.
4.  **Tombol Eksekusi:** Tombol "Kompres PDF" untuk menjalankan proses.
5.  **Status Bar / Label Log:** Menampilkan status seperti "Siap", "Sedang Memproses...", "Berhasil!", atau "Gagal".

## 5. Logika Backend (Subprocess)
*   **Penanganan Path Relatif (PENTING untuk PyInstaller):** Gunakan fungsi pembantu (helper) menggunakan `sys._MEIPASS` untuk menemukan lokasi aktual folder `assets` tempat `qpdf.exe` dan `gswin64c.exe` diekstrak saat berjalan sebagai `.exe` tunggal.
*   **Perintah QPDF (Mode Aman):**
    `assets/qpdf.exe --linearize --optimize-images "input_path.pdf" "output_path.pdf"`
*   **Perintah Ghostscript (Mode Ekstrem):**
    `assets/gswin64c.exe -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 -dPDFSETTINGS=/ebook -dNOPAUSE -dQUIET -dBATCH -sOutputFile="output_path.pdf" "input_path.pdf"`
*   **Proses Non-blocking:** Jalankan `subprocess` di dalam `threading.Thread` agar GUI tidak *freeze* saat proses kompresi berlangsung.

## 6. Instruksi Kompilasi (PyInstaller)
Setelah `main.py` selesai dan berfungsi, kompilasi menggunakan perintah berikut di terminal agar seluruh isi folder `assets` ikut terbawa ke dalam `.exe`:

```bash
pyinstaller --noconsole --onefile --add-data "assets;assets" main.py
# Denian Media Pro (v2.0.0)

**Denian Media Pro** (sebelumnya *Denian pdf Pro*) adalah aplikasi desktop kompresor media (PDF, Foto, dan Video) yang sangat cepat, aman, dan mudah digunakan. Dibangun menggunakan Python dan CustomTkinter, aplikasi ini kini mengusung desain **Neumorphism / Physical UI** yang modern, rapi, dan memanjakan mata.

Denian Media Pro bertindak sebagai *GUI wrapper* cerdas untuk *engine* kompresi terbaik di kelasnya:
- **QPDF & Ghostscript** untuk PDF (Aman/Lossless & Ekstrem).
- **FFmpeg** untuk Foto & Video (Berbagai level dan konversi format).

---

## 🔥 Fitur Baru di v2.0 (Massive Update!)

1. **Multi-Media Support (Tab Baru)**
   Tidak lagi hanya PDF! Sekarang Anda bisa mengompres **Foto** (JPG, PNG, WEBP, dll) dan **Video** (MP4, MKV, WEBM) dengan sangat cepat melalui tab khusus.

2. **Opsi Kompresi Lengkap & Konversi Format**
   - **Foto & Video:** Pilih antara 3 level (Kualitas Tinggi, Seimbang, Ekstrem).
   - Mendukung konversi format otomatis saat kompresi (misal: convert Foto ke `.webp` atau Video ke `.mp4`).

3. **Smart Batch Processing & Skip Exists**
   Kini Anda bisa memasukkan satu folder utuh! Aplikasi akan otomatis mendeteksi file yang sudah pernah dikompres di folder tujuan dan melewatinya (skip) secara pintar untuk menghemat waktu.

4. **Skeuomorphic & Neumorphic UI Design**
   Perombakan total antarmuka:
   - Panel dan tombol dengan gaya fisik/timbul (Skeuomorphism).
   - **Draggable Splitter**: Tarik garis pembatas antara daftar Input dan Output sesuai selera Anda!
   - Progress bar *real-time* yang sangat akurat untuk pemrosesan video berdurasi panjang (FFmpeg parsing).

5. **Bulletproof Engine (Anti-Crash)**
   GUI tidak akan pernah "Not Responding" berkat sistem pemrosesan multithreading yang aman. Terdapat juga tombol **Force Stop** jika Anda ingin membatalkan kompresi massal seketika.

---

## 🚀 Cara Penggunaan (Instalasi Sangat Mudah!)

1. Unduh file `Setup_DenianMediaPro.exe` dari halaman **[Releases](https://github.com/seyan88/Denian_pdf_Pro.exe/releases)**.
2. **Klik 2 kali (Double-Click)** file `.exe` tersebut untuk menginstal.
3. Setelah instalasi selesai, aplikasi sudah langsung siap digunakan! Buka melalui *Start Menu* atau *Shortcut Desktop* Anda.
*(Semua tools seperti FFmpeg, QPDF, dan Ghostscript sudah tertanam otomatis di dalamnya, Anda tidak perlu repot instal apa-apa lagi!)*

---

## 🛠️ Untuk Developer (Build from Source)

Jika Anda ingin mengompilasi ulang aplikasi ini menjadi `.exe` installer sendiri:
1. Pastikan Anda sudah menginstal **PyInstaller** dan **Inno Setup (v6/v7)**.
2. Jalankan skrip rilis otomatis yang sudah disediakan:
   ```bash
   python build_release.py
   ```
3. Skrip akan otomatis membungkus semua file Python, mengaitkan folder `assets/`, dan memanggil Inno Setup Compiler (`ISCC`) untuk melahirkan `Setup_DenianMediaPro.exe` di folder `Releases/`.

---

*Terima kasih telah menggunakan tools ini. Jika aplikasi ini membantu produktivitas Anda, Anda bisa mendukung kreator melalui tautan **Traktir Kopi** di dalam aplikasi.* ☕🐈‍⬛

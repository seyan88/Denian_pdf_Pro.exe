import os
import sys
import subprocess

def run_pyinstaller():
    print("[1/3] Menjalankan PyInstaller untuk membuat file .exe...")
    cmd = [
        "pyinstaller",
        "--noconsole",
        "--onefile",
        "--name", "Denian Media Pro",
        "--icon=assets/logo.ico",
        "--add-data", "assets;assets",
        "main.py"
    ]
    
    # Gunakan shell=True untuk Windows jika command berupa string, 
    # tapi menggunakan list lebih aman jika tanpa shell.
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print("ERROR: Gagal saat kompilasi PyInstaller!")
        print(result.stderr)
        sys.exit(1)
    print("OK: PyInstaller selesai. Eksekutabel berada di folder dist/.")

def generate_iss():
    print("[2/3] Membuat konfigurasi Inno Setup (installer_config.iss)...")
    iss_content = """[Setup]
AppName=Denian Media Pro
AppVersion=2.0.0
AppPublisher=Denian
DefaultDirName={autopf}\\Denian Media Pro
DefaultGroupName=Denian Media Pro
OutputDir=Releases
OutputBaseFilename=Setup_DenianMediaPro
SetupIconFile=assets\\logo.ico
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "dist\\Denian Media Pro.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\\Denian Media Pro"; Filename: "{app}\\Denian Media Pro.exe"
Name: "{autodesktop}\\Denian Media Pro"; Filename: "{app}\\Denian Media Pro.exe"; Tasks: desktopicon
"""
    with open("installer_config.iss", "w", encoding="utf-8") as f:
        f.write(iss_content)
    
    # Buat folder Releases jika belum ada
    os.makedirs("Releases", exist_ok=True)
    print("OK: File installer_config.iss berhasil dibuat.")

def run_inno_setup():
    print("[3/3] Mengompilasi Setup Installer menggunakan ISCC...")
    
    possible_paths = [
        r"C:\Program Files\Inno Setup 7\ISCC.exe",
        r"C:\Program Files (x86)\Inno Setup 7\ISCC.exe",
        os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Programs', 'Inno Setup 7', 'ISCC.exe'),
        r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
        r"C:\Program Files\Inno Setup 6\ISCC.exe",
        os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Programs', 'Inno Setup 6', 'ISCC.exe')
    ]
    
    iscc_path = None
    for p in possible_paths:
        if os.path.exists(p):
            iscc_path = p
            break
            
    if not iscc_path:
        print("ERROR: Inno Setup Compiler (ISCC) tidak ditemukan di jalur manapun!")
        print("Pastikan Inno Setup 6 terpasang dengan benar di komputer Anda.")
        sys.exit(1)
        
    cmd = [iscc_path, "installer_config.iss"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print("ERROR: Gagal saat melakukan kompilasi Inno Setup!")
        print(result.stdout)
        print(result.stderr)
        sys.exit(1)
        
    print("OK: Inno Setup Compiler selesai memproses!")
    # Tampilkan sedikit ringkasan dari output Inno Setup
    for line in result.stdout.splitlines():
        if "Successful compile" in line or "Resulting Setup program filename is" in line:
            print(f"INFO: {line.strip()}")

if __name__ == "__main__":
    # Force UTF-8 print for Windows terminal safety (optional, but removing emojis is safer)
    print(">>> Memulai Proses Build Rilis Otomatis [Denian Media Pro] <<<")
    print("=" * 60)
    
    run_pyinstaller()
    generate_iss()
    run_inno_setup()
    
    print("=" * 60)
    print("SUKSES! Semua proses selesai tanpa error.")
    print(f"File Installer Anda siap di: {os.path.abspath('Releases/Setup_DenianMediaPro.exe')}")

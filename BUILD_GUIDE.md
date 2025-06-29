# 🏗️ Build Guide - Endless Sky Translator

This comprehensive guide explains how to compile the **Endless Sky Translator** into executable files for different platforms:
- **Windows**: `.exe` executable
- **Linux**: `.AppImage` portable application

## 📋 Prerequisites

### Common Requirements
- **Python 3.6 or higher** (tested with Python 3.11.9)
- **Git** (for cloning the repository)
- **Internet connection** (for downloading dependencies)

### Platform-Specific Requirements

#### Windows (.exe)
- **Python 3.6+** with pip
- **PowerShell** or **Command Prompt**
- **Docker Desktop** (optional, for cross-compilation)

#### Linux (Native AppImage)
- **Ubuntu 18.04+** or equivalent
- **Python 3.6+** with pip3
- **wget, curl, file** utilities
- **ImageMagick** (for icon conversion)
- **fuse** (for AppImage runtime)

#### Cross-Platform (Docker Method)
- **Docker** installed and running
- **8GB+ RAM** recommended
- **5GB+ free disk space**

## 🚀 Build Methods Overview

| Method | Platform | Output | Difficulty | Speed |
|--------|----------|--------|------------|-------|
| **Windows Native** | Windows | `.exe` | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Linux Native** | Linux | `.AppImage` | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Docker Cross-Build** | Any | `.AppImage` | ⭐⭐ | ⭐⭐⭐ |

---

## 💻 Method 1: Windows Native Build (.exe)

### Step-by-Step Process

#### 1. Clone and Setup
```powershell
# Clone the repository
git clone https://github.com/kroryan/endless-sky-translator.git
cd endless-sky-translator

# OR download and extract ZIP if you don't have git
```

#### 2. Clean Environment (IMPORTANT)
```powershell
# Remove problematic packages that cause conflicts
pip uninstall -y ray gpustack anthropic chromadb torch tensorflow numpy pandas scipy matplotlib
```

#### 3. Install Dependencies
```powershell
# Install required packages
pip install deep-translator googletrans==3.1.0a0 requests chardet pyinstaller pillow
```

#### 4. Convert Icon (REQUIRED)
```powershell
# Convert WebP icon to ICO format
python convert_icon.py
```
**⚠️ Critical**: Without this step, the executable won't have the proper icon.

#### 5. Clean Previous Builds
```powershell
# Remove previous build artifacts
if (Test-Path "build") { Remove-Item -Path "build" -Recurse -Force }
if (Test-Path "dist") { Remove-Item -Path "dist" -Recurse -Force }
if (Test-Path "__pycache__") { Remove-Item -Path "__pycache__" -Recurse -Force }
```

#### 6. Compile Executable
```powershell
# TESTED AND WORKING COMMAND
pyinstaller --onefile --windowed --name "Endless_Sky_Translator" --add-data "translator.py;." --add-data "translations.py;." --add-data "translator_gui.py;." --hidden-import "tkinter" --hidden-import "tkinter.ttk" --hidden-import "tkinter.filedialog" --hidden-import "tkinter.messagebox" --hidden-import "tkinter.scrolledtext" --hidden-import "googletrans" --hidden-import "deep_translator" --hidden-import "requests" --hidden-import "chardet" --icon="endless_sky_translator.ico" run_gui.py
```

#### 7. Locate Your Executable
```powershell
# Your .exe file will be here:
ls dist\Endless_Sky_Translator.exe
```

**🎉 Success!** You now have `dist\Endless_Sky_Translator.exe` ready to distribute.

---

## 🐧 Method 2: Linux Native Build (.AppImage)

### Step-by-Step Process

#### 1. System Preparation (Ubuntu/Debian)
```bash
# Update system
sudo apt update

# Install dependencies
sudo apt install -y python3 python3-pip python3-tk python3-dev wget curl file desktop-file-utils fuse imagemagick git

# For CentOS/RHEL/Fedora:
# sudo dnf install -y python3 python3-pip python3-tkinter python3-devel wget curl file desktop-file-utils fuse ImageMagick git
```

#### 2. Clone Repository
```bash
# Clone the project
git clone https://github.com/kroryan/endless-sky-translator.git
cd endless-sky-translator

# Make scripts executable
chmod +x build_appimage_linux.sh
```

#### 3. Install Python Dependencies
```bash
# Install required Python packages
pip3 install --user deep-translator googletrans==3.1.0a0 requests chardet pyinstaller pillow
```

#### 4. Install AppImage Tools
```bash
# Download and install appimagetool
wget -q https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage
chmod +x appimagetool-x86_64.AppImage
sudo mv appimagetool-x86_64.AppImage /usr/local/bin/appimagetool

# Verify installation
appimagetool --version
```

#### 5. Run Build Script
```bash
# Execute the build script
./build_appimage_linux.sh
```

#### 6. Test Your AppImage
```bash
# Your AppImage will be in dist/ folder
ls -la dist/Endless_Sky_Translator-x86_64.AppImage

# Make it executable and test
chmod +x dist/Endless_Sky_Translator-x86_64.AppImage
./dist/Endless_Sky_Translator-x86_64.AppImage
```

**🎉 Success!** You now have a portable AppImage that runs on most Linux distributions.

---

## 🐳 Method 3: Docker Cross-Build (Any Platform → AppImage)

This method allows you to build Linux AppImages from Windows, macOS, or Linux using Docker.

### Step-by-Step Process

#### 1. Install Docker
- **Windows/macOS**: Download Docker Desktop from [docker.com](https://www.docker.com/products/docker-desktop)
- **Linux**: Follow your distribution's Docker installation guide

#### 2. Clone Repository
```bash
# Windows (PowerShell)
git clone https://github.com/kroryan/endless-sky-translator.git
cd endless-sky-translator

# Linux/macOS (Terminal)
git clone https://github.com/kroryan/endless-sky-translator.git
cd endless-sky-translator
```

#### 3. Build with Docker
```bash
# For Windows (PowerShell):
cd "d:\Program Files (x86)\Steam\steamapps\common\Endless Sky\traductor_automatico"
docker build -t endless-sky-translator-appimage -f ./Dockerfile.appimage .

# For Linux/macOS (Terminal):
docker build -t endless-sky-translator-appimage -f ./Dockerfile.appimage .
```

#### 4. Extract the AppImage
```bash
# Create a temporary container and copy the AppImage
docker create --name temp-container endless-sky-translator-appimage
docker cp temp-container:/app/dist/Endless_Sky_Translator-x86_64.AppImage ./dist/
docker rm temp-container

# Verify the AppImage was copied
ls -la dist/Endless_Sky_Translator-x86_64.AppImage
```

#### 5. Test on Linux
```bash
# On a Linux system, make it executable and run
chmod +x dist/Endless_Sky_Translator-x86_64.AppImage
./dist/Endless_Sky_Translator-x86_64.AppImage
```

**🎉 Success!** You've cross-compiled a Linux AppImage from any platform.

---

## 🗂️ Output Structure

After successful build, your directory will look like:

```
endless-sky-translator/
├── dist/                                   # 📁 Final executables
│   ├── Endless_Sky_Translator.exe          # 🎯 Windows executable
│   └── Endless_Sky_Translator-x86_64.AppImage  # 🐧 Linux AppImage
├── build/                                  # 📁 Temporary build files
├── endless_sky_translator.ico              # 🎨 Application icon
├── Endless_Sky_Translator.spec             # ⚙️ PyInstaller spec file
├── build_appimage_linux.sh                # 📜 Linux build script
├── Dockerfile.appimage                     # 🐳 Docker build config
└── ... (source files)
```

---

## 📊 File Sizes and Performance

| Platform | File Size | Startup Time | RAM Usage |
|----------|-----------|--------------|-----------|
| Windows .exe | ~25-35 MB | 2-4 seconds | ~50-80 MB |
| Linux AppImage | ~12-20 MB | 1-3 seconds | ~40-70 MB |

---

## 🛠️ Troubleshooting

### Common Issues and Solutions

#### ❌ "Python not found"
**Windows**:
```powershell
# Reinstall Python with PATH option checked
# Download from: https://www.python.org/downloads/
```

**Linux**:
```bash
sudo apt install python3 python3-pip  # Ubuntu/Debian
sudo dnf install python3 python3-pip  # Fedora/CentOS
```

#### ❌ "PyInstaller not found"
```bash
pip install pyinstaller --upgrade
# or
pip3 install pyinstaller --upgrade
```

#### ❌ "ModuleNotFoundError: No module named 'X'"
```bash
# Install missing dependencies
pip install -r requirements.txt

# For specific modules:
pip install deep-translator googletrans requests chardet pillow
```

#### ❌ "Docker build failed"
```bash
# Make sure Docker is running
docker --version

# On Windows, restart Docker Desktop
# On Linux, start Docker service:
sudo systemctl start docker
```

#### ❌ "AppImage won't run on Linux"
```bash
# Install FUSE if missing
sudo apt install fuse  # Ubuntu/Debian
sudo dnf install fuse  # Fedora/CentOS

# Make AppImage executable
chmod +x Endless_Sky_Translator-x86_64.AppImage

# Try running with --appimage-extract-and-run
./Endless_Sky_Translator-x86_64.AppImage --appimage-extract-and-run
```

#### ❌ "Icon not showing in executable"
```bash
# Make sure icon conversion was successful
python convert_icon.py
ls endless_sky_translator.ico  # Should exist

# Then rebuild executable
```

#### ❌ "Executable is too large"
The executables are optimized but include the Python runtime. This is normal for PyInstaller builds.

#### ❌ "Antivirus flags executable as suspicious"
This is common with PyInstaller executables. The executable is safe - you can:
1. Add an exclusion in your antivirus
2. Upload to VirusTotal.com to verify safety
3. Build from source code yourself

---

## 🎯 Advanced Build Options

### Custom Icon
Replace `icono.webp` with your own image and run:
```bash
python convert_icon.py
```

### Debugging Mode
Add `--debug=all` to PyInstaller command for verbose output:
```bash
pyinstaller --debug=all --onefile ... (rest of command)
```

### Console Version
Remove `--windowed` flag to keep console window visible:
```bash
pyinstaller --onefile --name "Endless_Sky_Translator_Console" ... (rest of command)
```

### Multiple Files (Instead of Single Executable)
Remove `--onefile` flag to create a directory with multiple files:
```bash
pyinstaller --windowed --name "Endless_Sky_Translator" ... (rest of command)
```

---

## 🚀 Quick Start Summary

### For Windows Users:
```powershell
git clone https://github.com/kroryan/endless-sky-translator.git
cd endless-sky-translator
pip install deep-translator googletrans==3.1.0a0 requests chardet pyinstaller pillow
python convert_icon.py
pyinstaller --onefile --windowed --name "Endless_Sky_Translator" --add-data "translator.py;." --add-data "translations.py;." --add-data "translator_gui.py;." --hidden-import "tkinter" --hidden-import "tkinter.ttk" --hidden-import "tkinter.filedialog" --hidden-import "tkinter.messagebox" --hidden-import "tkinter.scrolledtext" --hidden-import "googletrans" --hidden-import "deep_translator" --hidden-import "requests" --hidden-import "chardet" --icon="endless_sky_translator.ico" run_gui.py
```

### For Linux Users:
```bash
git clone https://github.com/kroryan/endless-sky-translator.git
cd endless-sky-translator
chmod +x build_appimage_linux.sh
./build_appimage_linux.sh
```

### For Docker Users (Any Platform):
```bash
git clone https://github.com/kroryan/endless-sky-translator.git
cd endless-sky-translator
docker build -t endless-sky-translator-appimage -f ./Dockerfile.appimage .
docker create --name temp-container endless-sky-translator-appimage
docker cp temp-container:/app/dist/Endless_Sky_Translator-x86_64.AppImage ./dist/
docker rm temp-container
```

---

## 📞 Support

If you encounter issues:

1. **Check Prerequisites**: Ensure all required software is installed
2. **Try Clean Build**: Remove `build/`, `dist/`, and `__pycache__/` directories
3. **Verify Dependencies**: Run `python run_gui.py` directly first
4. **Check GitHub Issues**: Visit the repository's issues page
5. **Create New Issue**: Include error messages and system information

**Repository**: [https://github.com/kroryan/endless-sky-translator](https://github.com/kroryan/endless-sky-translator)

---

## 🔒 Security Notes

- Executables are built from open source code
- No malicious code or data collection
- Antivirus false positives are common with PyInstaller
- All translations are done via Google Translate API
- No personal data is transmitted

Ready to build your executable! Choose your preferred method and follow the guide. 🚀

# 🏗️ Executable Build Guide

This document explains how to compile the **Endless Sky Translator** into an executable file (.exe for Windows, AppImage for Linux).

## 📋 Prerequisites

### For Windows (.exe)
- **Python 3.6 or higher** installed (tested with Python 3.11.9)
- **pip** working correctly
- **Internet** to download dependencies

### For Linux (AppImage)
- **Python 3.6 or higher**
- **pip3** installed
- **wget** to download tools
- **ImageMagick** (optional, for creating icons)

## 🚀 Build Methods

### Method 1: Clean Direct Build (RECOMMENDED)

This is the most reliable method that we tested and works 100%:

#### Windows - Complete Step by Step Process

1. **Clean Installation Environment**
   ```powershell
   # First, uninstall any problematic packages that cause conflicts
   pip uninstall -y ray gpustack anthropic chromadb torch tensorflow tensorflow-io-gcs-filesystem numpy pandas scipy matplotlib matplotlib-inline ipython ipython-pygments-lexers bitarray
   ```

2. **Install Required Dependencies**
   ```powershell
   pip install deep-translator googletrans==3.1.0a0 requests chardet pyinstaller pillow
   ```

3. **Convert Icon from WebP to ICO (REQUIRED for proper icon display)**
   ```powershell
   # This converts icono.webp to endless_sky_translator.ico
   python convert_icon.py
   ```
   **Note**: The icon conversion is ESSENTIAL. Without it, the executable won't have the proper icon.

4. **Clean Previous Builds**
   ```powershell
   if (Test-Path "build") { Remove-Item -Path "build" -Recurse -Force }
   if (Test-Path "dist") { Remove-Item -Path "dist" -Recurse -Force }
   if (Test-Path "__pycache__") { Remove-Item -Path "__pycache__" -Recurse -Force }
   ```

5. **Compile with PyInstaller (FINAL WORKING COMMAND)**
   ```powershell
   pyinstaller --onefile --windowed --name "Endless_Sky_Translator" --add-data "translator.py;." --add-data "translations.py;." --add-data "translator_gui.py;." --hidden-import "tkinter" --hidden-import "tkinter.ttk" --hidden-import "tkinter.filedialog" --hidden-import "tkinter.messagebox" --hidden-import "tkinter.scrolledtext" --hidden-import "googletrans" --hidden-import "deep_translator" --hidden-import "requests" --hidden-import "chardet" --icon="endless_sky_translator.ico" run_gui.py
   ```
   **IMPORTANT**: This exact command works and creates the executable with the proper icon. Make sure `endless_sky_translator.ico` exists before running.

6. **Find Your Executable**
   The compiled executable will be in `dist\Endless_Sky_Translator.exe`

### Method 2: Using Spec File (Advanced)

If you prefer using a .spec file for more control:

1. **Use the provided clean spec file**
   ```powershell
   pyinstaller endless_sky_translator_clean.spec
   ```

### Method 3: Automatic Build (Legacy)

#### Windows
1. **Double click** on `Build_Executable.bat`
2. **Wait** for the process to complete
3. **Look for** the `.exe` file in the `dist/` folder

#### Linux
```bash
chmod +x build_appimage.sh
./build_appimage.sh
```

### Method 4: Advanced Builder (Legacy)

```bash
# Install dependencies
pip install -r requirements.txt

# Run advanced builder
python build_advanced.py
```

#### Advanced Builder Options:
1. **Build executable** - Only create the .exe/.AppImage
2. **Build and package** - Create executable + complete distribution package
3. **Configuration only** - Create configuration files
4. **Show configuration** - Display current configuration

```bash
# Install PyInstaller
pip install pyinstaller

# Basic build
pyinstaller --onefile --windowed --name "Endless_Sky_Translator" run_gui.py

# Advanced build with configuration
python build_exe.py
```

## 📁 Generated Files

### Structure after compilation:
```
traductor_automatico/
├── dist/                               # 📁 Final executables
│   └── Endless_Sky_Translator.exe      # 🎯 Main executable
├── build/                              # 📁 Temporary files
├── Endless_Sky_Translator.spec         # ⚙️ PyInstaller configuration
├── icon.ico                            # 🎨 Application icon
└── Install_Endless_Sky_Translator.bat  # 📦 Automatic installer
```

### For distribution:
- **`dist/Endless_Sky_Translator.exe`** - Main executable
- **`README.md`** - Usage documentation
- **`Install_*.bat`** - Automatic installer (Windows only)

## ⚙️ Advanced Configuration

### `build_config.json` File

You can customize the build by editing this file:

```json
{
  "app": {
    "name": "Endless Sky Translator",
    "version": "1.0.0",
    "main_script": "run_gui.py"
  },
  "build": {
    "output_dir": "dist",
    "one_file": true,
    "windowed": true,
    "console": false
  },
  "hidden_imports": [
    "tkinter",
    "googletrans",
    "requests"
  ]
}
```

### Icon Customization

1. **Automatic**: The script creates a basic icon
2. **Manual**: Place your `icon.ico` file in the directory
3. **No icon**: Remove the reference in the configuration

## 🎯 Expected File Sizes

| Platform | Typical Size | Content |
|----------|-------------|---------|
| Windows .exe | 25-40 MB | Python + dependencies + application |
| Linux AppImage | 30-50 MB | Python + dependencies + application |

## 🛠️ Troubleshooting

### Error: "ModuleNotFoundError"
```bash
# Solution: Install dependencies
pip install -r requirements.txt
```

### Error: "PyInstaller not found"
```bash
# Solution: Install PyInstaller
pip install pyinstaller
```

### Error: "Python not found"
- **Windows**: Reinstall Python from python.org, check "Add to PATH"
- **Linux**: `sudo apt install python3 python3-pip`

### Error: "Executable too large"
```bash
# Use UPX to compress (optional)
pip install upx-python
# The script uses it automatically if available
```

### Error: "Missing module in executable"
Edit `build_config.json` and add the module to `hidden_imports`:
```json
"hidden_imports": [
  "tkinter",
  "googletrans",
  "your_missing_module"
]
```

## 📊 Method Comparison

| Method | Ease | Control | Speed | Recommended for |
|--------|------|---------|-------|-----------------|
| `.bat` automatic | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ | End users |
| Advanced builder | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | Developers |
| PyInstaller manual | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | Experts |

## 🎮 Executable Distribution

### For end users:
1. **Copy** the `.exe` file from the `dist/` folder
2. **No need** for Python to be installed on target machine
3. **Run** directly with double click
4. **Include** the README.md for instructions

### For developers:
1. **Complete package** with `build_advanced.py` option 2
2. **Includes** source code, documentation and installer
3. **Facilitates** future modifications

## 🔒 Security and Antivirus

### Common false positives:
- **Some antivirus** may flag PyInstaller executables as suspicious
- **This is normal** for Python-packaged applications
- **Solution**: Add exclusion in antivirus or distribute source code

### To avoid issues:
1. **Test** on clean machine to verify
2. **Use** services like VirusTotal to verify
3. **Document** clearly that it's a game translator

## 🌐 Cross-Platform Support

### Windows
- ✅ **Fully supported**
- ✅ **Executable .exe**
- ✅ **Automatic installer**

### Linux  
- ✅ **Supported with AppImage**
- ✅ **Portable without installation**
- ⚠️ **Requires additional tools**

### macOS
- ⚠️ **Experimental**
- ⚠️ **Requires manual modifications**
- 📝 **Not included in automatic scripts**

## 📞 Support

If you have compilation problems:

1. **Verify** that all files are present
2. **Run** `python run_gui.py` directly first
3. **Check** that dependencies are installed
4. **Use** the automatic `.bat` method if in doubt

## 📝 Technical Notes

### PyInstaller
- **Packages** Python + dependencies in a single file
- **Automatically detects** most dependencies
- **Creates** native executables for each platform

### Included optimizations:
- ✅ **UPX compression** to reduce size
- ✅ **Exclusion** of unnecessary modules
- ✅ **Inclusion** of necessary data files
- ✅ **Custom** icons

Ready to create your executable! 🚀

#!/bin/bash
# Build AppImage for Endless Sky Translator on Linux
# This script must be run on a Linux system

set -e  # Exit on any error

echo "🐧 Building Endless Sky Translator AppImage for Linux"
echo "=================================================="

# Check if we're on Linux
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    echo "❌ This script must be run on Linux to create an AppImage"
    echo "💡 Use build_exe.py on Windows to create a .exe file instead"
    exit 1
fi

# Check dependencies
echo "🔍 Checking dependencies..."

if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is required but not installed"
    exit 1
fi

if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is required but not installed"
    exit 1
fi

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip3 install --user deep-translator googletrans==3.1.0a0 requests chardet pyinstaller pillow

# Convert icon (if needed)
echo "🎨 Converting icon..."
if [ -f "icono.webp" ]; then
    python3 convert_icon.py
    echo "✅ Icon converted successfully"
else
    echo "⚠️ Source icon icono.webp not found, skipping icon conversion"
fi

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf build/ dist/ __pycache__/ *.spec

# Build with PyInstaller (Linux executable)
echo "🔨 Building Linux executable with PyInstaller..."
pyinstaller --onefile \
    --windowed \
    --name "Endless_Sky_Translator" \
    --add-data "translator.py:." \
    --add-data "translations.py:." \
    --add-data "translator_gui.py:." \
    --hidden-import "tkinter" \
    --hidden-import "tkinter.ttk" \
    --hidden-import "tkinter.filedialog" \
    --hidden-import "tkinter.messagebox" \
    --hidden-import "tkinter.scrolledtext" \
    --hidden-import "googletrans" \
    --hidden-import "deep_translator" \
    --hidden-import "requests" \
    --hidden-import "chardet" \
    $([ -f "endless_sky_translator.ico" ] && echo "--icon=endless_sky_translator.ico" || echo "") \
    run_gui.py

if [ $? -eq 0 ]; then
    echo "✅ Linux executable built successfully!"
    echo "📁 Executable location: dist/Endless_Sky_Translator"
else
    echo "❌ Build failed!"
    exit 1
fi

# Check if AppImage tools are available
echo ""
echo "🔍 Checking for AppImage creation tools..."

if command -v appimagetool &> /dev/null; then
    echo "✅ appimagetool found - Creating AppImage..."
    
    # Create AppDir structure
    APPDIR="Endless_Sky_Translator.AppDir"
    mkdir -p "$APPDIR/usr/bin"
    mkdir -p "$APPDIR/usr/share/applications"
    mkdir -p "$APPDIR/usr/share/icons/hicolor/256x256/apps"
    
    # Copy executable
    cp "dist/Endless_Sky_Translator" "$APPDIR/usr/bin/"
    
    # Create desktop file
    cat > "$APPDIR/usr/share/applications/endless-sky-translator.desktop" << EOF
[Desktop Entry]
Type=Application
Name=Endless Sky Translator
Comment=Translation tool for Endless Sky game files
Exec=Endless_Sky_Translator
Icon=endless-sky-translator
Categories=Utility;Game;
Terminal=false
EOF
    
    # Copy icon if available
    if [ -f "endless_sky_translator.ico" ]; then
        # Convert ICO to PNG for AppImage (requires ImageMagick)
        if command -v convert &> /dev/null; then
            convert "endless_sky_translator.ico[0]" "$APPDIR/usr/share/icons/hicolor/256x256/apps/endless-sky-translator.png"
        else
            echo "⚠️ ImageMagick not found, skipping icon conversion"
        fi
    fi
    
    # Create AppRun script
    cat > "$APPDIR/AppRun" << 'EOF'
#!/bin/bash
HERE="$(dirname "$(readlink -f "${0}")")"
export PATH="${HERE}/usr/bin:${PATH}"
exec "${HERE}/usr/bin/Endless_Sky_Translator" "$@"
EOF
    chmod +x "$APPDIR/AppRun"
    
    # Copy desktop file to root
    cp "$APPDIR/usr/share/applications/endless-sky-translator.desktop" "$APPDIR/"
    
    # Copy icon to root
    if [ -f "$APPDIR/usr/share/icons/hicolor/256x256/apps/endless-sky-translator.png" ]; then
        cp "$APPDIR/usr/share/icons/hicolor/256x256/apps/endless-sky-translator.png" "$APPDIR/"
    fi
    
    # Create AppImage
    appimagetool "$APPDIR" "Endless_Sky_Translator-x86_64.AppImage"
    
    if [ $? -eq 0 ]; then
        echo "🎉 AppImage created successfully!"
        echo "📁 AppImage location: Endless_Sky_Translator-x86_64.AppImage"
        echo ""
        echo "🚀 To run the AppImage:"
        echo "   chmod +x Endless_Sky_Translator-x86_64.AppImage"
        echo "   ./Endless_Sky_Translator-x86_64.AppImage"
    else
        echo "❌ AppImage creation failed!"
        exit 1
    fi
else
    echo "⚠️ appimagetool not found - only Linux executable was created"
    echo "💡 To create an AppImage, install appimagetool:"
    echo "   wget https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage"
    echo "   chmod +x appimagetool-x86_64.AppImage"
    echo "   sudo mv appimagetool-x86_64.AppImage /usr/local/bin/appimagetool"
    echo "   Then run this script again"
fi

echo ""
echo "✅ Build process completed!"

#!/bin/bash

# Constructor de AppImage para Traductor de Endless Sky
# Requiere: Python 3.6+, pip, AppImageTool

set -e

echo "========================================="
echo "  Traductor Endless Sky - AppImage Build"
echo "========================================="
echo

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Funciones helper
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

# Verificar Python
print_info "Verificando Python..."
if ! command -v python3 &> /dev/null; then
    print_error "Python3 no encontrado"
    print_info "Instala Python3: sudo apt install python3 python3-pip"
    exit 1
fi

python_version=$(python3 --version | cut -d' ' -f2)
print_success "Python $python_version encontrado"

# Verificar pip
if ! command -v pip3 &> /dev/null; then
    print_error "pip3 no encontrado"
    print_info "Instala pip3: sudo apt install python3-pip"
    exit 1
fi

# Instalar dependencias del sistema
print_info "Verificando dependencias del sistema..."
if ! command -v wget &> /dev/null; then
    print_warning "wget no encontrado, instalando..."
    sudo apt update && sudo apt install -y wget
fi

# Crear entorno virtual
print_info "Creando entorno virtual..."
if [ -d "venv" ]; then
    rm -rf venv
fi

python3 -m venv venv
source venv/bin/activate

# Actualizar pip e instalar dependencias
print_info "Instalando dependencias Python..."
pip install --upgrade pip
pip install -r requirements.txt

# Crear estructura AppDir
print_info "Creando estructura AppDir..."
APP_DIR="Traductor_Endless_Sky.AppDir"

if [ -d "$APP_DIR" ]; then
    rm -rf "$APP_DIR"
fi

mkdir -p "$APP_DIR/usr/bin"
mkdir -p "$APP_DIR/usr/lib"
mkdir -p "$APP_DIR/usr/share/applications"
mkdir -p "$APP_DIR/usr/share/pixmaps"

# Crear ejecutable principal
print_info "Creando ejecutable principal..."
cat > "$APP_DIR/usr/bin/traductor-endless-sky" << 'EOF'
#!/bin/bash
APPDIR="$(dirname "$(readlink -f "${0}")")/../.."
export PYTHONPATH="$APPDIR/usr/lib/python3/site-packages:$PYTHONPATH"
cd "$APPDIR/usr/bin"
python3 run_gui.py
EOF

chmod +x "$APP_DIR/usr/bin/traductor-endless-sky"

# Copiar archivos de la aplicación
print_info "Copiando archivos de la aplicación..."
cp run_gui.py "$APP_DIR/usr/bin/"
cp translator.py "$APP_DIR/usr/bin/"
cp translator_gui.py "$APP_DIR/usr/bin/"
cp requirements.txt "$APP_DIR/usr/bin/"
cp README.md "$APP_DIR/usr/bin/"

# Copiar dependencias Python
print_info "Copiando dependencias Python..."
pip_site_packages=$(python3 -c "import site; print(site.getsitepackages()[0])")
cp -r "$pip_site_packages"/* "$APP_DIR/usr/lib/python3/site-packages/" 2>/dev/null || true

# Crear archivo .desktop
print_info "Creando archivo .desktop..."
cat > "$APP_DIR/usr/share/applications/traductor-endless-sky.desktop" << EOF
[Desktop Entry]
Type=Application
Name=Traductor Endless Sky
Comment=Traductor automático para el juego Endless Sky
Icon=traductor-endless-sky
Exec=traductor-endless-sky
Categories=Game;Utility;
EOF

# Crear AppRun
print_info "Creando AppRun..."
cat > "$APP_DIR/AppRun" << 'EOF'
#!/bin/bash
APPDIR="$(dirname "$(readlink -f "${0}")")"
export PATH="$APPDIR/usr/bin:$PATH"
export LD_LIBRARY_PATH="$APPDIR/usr/lib:$LD_LIBRARY_PATH"
export PYTHONPATH="$APPDIR/usr/lib/python3/site-packages:$PYTHONPATH"
cd "$APPDIR/usr/bin"
exec python3 run_gui.py "$@"
EOF

chmod +x "$APP_DIR/AppRun"

# Crear ícono simple
print_info "Creando ícono..."
if command -v convert &> /dev/null; then
    # Si ImageMagick está disponible, crear un ícono simple
    convert -size 256x256 xc:'#0078d7' \
            -gravity center -pointsize 48 -fill white \
            -annotate +0+0 'ES\nT' \
            "$APP_DIR/usr/share/pixmaps/traductor-endless-sky.png"
    
    cp "$APP_DIR/usr/share/pixmaps/traductor-endless-sky.png" "$APP_DIR/"
else
    # Crear un ícono de texto simple
    echo "ES" > "$APP_DIR/traductor-endless-sky.png"
fi

# Symlinks requeridos
ln -sf usr/share/applications/traductor-endless-sky.desktop "$APP_DIR/"
ln -sf usr/share/pixmaps/traductor-endless-sky.png "$APP_DIR/" 2>/dev/null || true

# Descargar AppImageTool si no existe
APPIMAGE_TOOL="./appimagetool-x86_64.AppImage"
if [ ! -f "$APPIMAGE_TOOL" ]; then
    print_info "Descargando AppImageTool..."
    wget -O "$APPIMAGE_TOOL" "https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage"
    chmod +x "$APPIMAGE_TOOL"
fi

# Crear AppImage
print_info "Creando AppImage..."
ARCH=x86_64 "$APPIMAGE_TOOL" "$APP_DIR" "Traductor_Endless_Sky-x86_64.AppImage"

if [ $? -eq 0 ]; then
    print_success "AppImage creado exitosamente!"
    print_info "Archivo: $(pwd)/Traductor_Endless_Sky-x86_64.AppImage"
    
    # Mostrar información del archivo
    ls -lh "Traductor_Endless_Sky-x86_64.AppImage"
    
    echo
    print_info "Para usar el AppImage:"
    print_info "1. Haz el archivo ejecutable: chmod +x Traductor_Endless_Sky-x86_64.AppImage"
    print_info "2. Ejecuta: ./Traductor_Endless_Sky-x86_64.AppImage"
    
else
    print_error "Error creando AppImage"
    exit 1
fi

# Limpiar
read -p "¿Eliminar archivos temporales? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_info "Limpiando archivos temporales..."
    rm -rf "$APP_DIR"
    rm -rf venv
    rm -f "$APPIMAGE_TOOL"
    print_success "Limpieza completada"
fi

print_success "¡Proceso completado!"

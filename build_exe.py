#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para compilar el Traductor de Endless Sky a ejecutable
Usando PyInstaller para crear .exe (Windows) y ejecutables Linux
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def install_pyinstaller():
    """Instala PyInstaller si no está disponible"""
    try:
        import PyInstaller
        print("✅ PyInstaller ya está instalado")
        return True
    except ImportError:
        print("📦 Instalando PyInstaller...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
            print("✅ PyInstaller instalado correctamente")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Error instalando PyInstaller: {e}")
            return False

def build_executable():
    """Construye el ejecutable usando PyInstaller"""
    
    if not install_pyinstaller():
        return False
    
    print("\n🚀 Iniciando construcción del ejecutable...")
    
    # Directorio actual
    current_dir = Path(__file__).parent
    
    # Nombre del ejecutable
    exe_name = "Traductor_Endless_Sky"
    
    # Comando PyInstaller
    cmd = [
        "pyinstaller",
        "--onefile",  # Un solo archivo ejecutable
        "--windowed",  # Sin ventana de consola (GUI)
        "--name", exe_name,
        "--icon=icon.ico" if os.path.exists("icon.ico") else "",
        "--add-data", "requirements.txt;.",  # Incluir requirements
        "--add-data", "README.md;.",  # Incluir documentación
        "--distpath", "./dist",  # Directorio de salida
        "--workpath", "./build",  # Directorio de trabajo temporal
        "--specpath", "./",  # Directorio para el archivo .spec
        "run_gui.py"  # Archivo principal
    ]
    
    # Remover elementos vacíos
    cmd = [arg for arg in cmd if arg]
    
    try:
        print(f"🔨 Ejecutando: {' '.join(cmd)}")
        result = subprocess.run(cmd, cwd=current_dir, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Ejecutable creado exitosamente!")
            exe_path = current_dir / "dist" / f"{exe_name}.exe"
            if exe_path.exists():
                print(f"📁 Ejecutable ubicado en: {exe_path}")
                print(f"📏 Tamaño: {exe_path.stat().st_size / (1024*1024):.1f} MB")
            return True
        else:
            print("❌ Error durante la construcción:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Error ejecutando PyInstaller: {e}")
        return False

def create_spec_file():
    """Crea un archivo .spec personalizado para mayor control"""
    
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['run_gui.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('requirements.txt', '.'),
        ('README.md', '.'),
        ('translator.py', '.'),
        ('translator_gui.py', '.'),
    ],
    hiddenimports=[
        'tkinter',
        'tkinter.ttk',
        'tkinter.filedialog',
        'tkinter.messagebox',
        'tkinter.scrolledtext',
        'googletrans',
        'requests',
        'chardet',
        'deep_translator',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Traductor_Endless_Sky',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # GUI sin consola
    disable_windowed_traceback=False,
    icon='icon.ico' if os.path.exists('icon.ico') else None,
)
'''
    
    with open("Traductor_Endless_Sky.spec", "w", encoding="utf-8") as f:
        f.write(spec_content)
    
    print("✅ Archivo .spec creado: Traductor_Endless_Sky.spec")

def build_with_spec():
    """Construye usando el archivo .spec personalizado"""
    
    create_spec_file()
    
    cmd = ["pyinstaller", "Traductor_Endless_Sky.spec"]
    
    try:
        print("🔨 Construyendo con archivo .spec personalizado...")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Ejecutable creado exitosamente con .spec!")
            return True
        else:
            print("❌ Error durante la construcción con .spec:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def create_icon():
    """Crea un ícono simple para el ejecutable"""
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        # Crear imagen de 256x256
        size = 256
        img = Image.new('RGBA', (size, size), (0, 120, 215, 255))
        draw = ImageDraw.Draw(img)
        
        # Dibujar forma simple
        margin = 40
        draw.rectangle([margin, margin, size-margin, size-margin], 
                      fill=(255, 255, 255, 255), outline=(0, 0, 0, 255), width=3)
        
        # Texto
        try:
            font = ImageFont.truetype("arial.ttf", 40)
        except:
            font = ImageFont.load_default()
        
        text = "ES\nT"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (size - text_width) // 2
        y = (size - text_height) // 2
        
        draw.text((x, y), text, fill=(0, 120, 215, 255), font=font, align="center")
        
        # Guardar como ICO
        img.save("icon.ico", format="ICO", sizes=[(256, 256), (128, 128), (64, 64), (32, 32), (16, 16)])
        print("✅ Ícono creado: icon.ico")
        return True
        
    except ImportError:
        print("⚠️ PIL/Pillow no disponible, omitiendo creación de ícono")
        return False
    except Exception as e:
        print(f"⚠️ Error creando ícono: {e}")
        return False

def create_installer_script():
    """Crea un script para instalar dependencias automáticamente"""
    
    installer_content = '''@echo off
echo ========================================
echo  Traductor de Endless Sky - Instalador
echo ========================================
echo.

echo Verificando Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python no encontrado. Por favor instala Python 3.6+ desde python.org
    pause
    exit /b 1
)

echo ✅ Python encontrado

echo.
echo Instalando dependencias...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo ❌ Error instalando dependencias
    pause
    exit /b 1
)

echo ✅ Dependencias instaladas correctamente

echo.
echo Construyendo ejecutable...
python build_exe.py

echo.
echo ✅ Proceso completado
pause
'''
    
    with open("instalar_y_compilar.bat", "w", encoding="utf-8") as f:
        f.write(installer_content)
    
    print("✅ Script de instalación creado: instalar_y_compilar.bat")

def clean_build_files():
    """Limpia archivos temporales de construcción"""
    
    dirs_to_clean = ["build", "__pycache__"]
    files_to_clean = ["*.spec"]
    
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"🧹 Eliminado directorio: {dir_name}")
    
    import glob
    for pattern in files_to_clean:
        for file in glob.glob(pattern):
            os.remove(file)
            print(f"🧹 Eliminado archivo: {file}")

def main():
    """Función principal del constructor"""
    
    print("🏗️ Constructor de Ejecutable - Traductor Endless Sky")
    print("=" * 50)
    
    # Verificar que estamos en el directorio correcto
    if not os.path.exists("run_gui.py"):
        print("❌ Error: No se encuentra run_gui.py en el directorio actual")
        print("   Asegúrate de ejecutar este script en el directorio del traductor")
        return False
    
    # Crear ícono si es posible
    create_icon()
    
    # Crear script de instalación
    create_installer_script()
    
    print("\n🎯 Selecciona el método de construcción:")
    print("1. Construcción rápida (recomendado)")
    print("2. Construcción con archivo .spec personalizado")
    print("3. Solo crear archivos de configuración")
    print("4. Limpiar archivos temporales")
    
    choice = input("\nOpción (1-4): ").strip()
    
    if choice == "1":
        success = build_executable()
    elif choice == "2":
        success = build_with_spec()
    elif choice == "3":
        create_spec_file()
        create_installer_script()
        print("✅ Archivos de configuración creados")
        success = True
    elif choice == "4":
        clean_build_files()
        print("✅ Archivos temporales eliminados")
        success = True
    else:
        print("❌ Opción inválida")
        success = False
    
    if success and choice in ["1", "2"]:
        print("\n🎉 ¡Construcción completada!")
        print("\n📋 Archivos generados:")
        
        dist_dir = Path("dist")
        if dist_dir.exists():
            for file in dist_dir.iterdir():
                print(f"   📁 {file}")
                
        print("\n💡 Para distribuir:")
        print("   1. Copia el archivo .exe de la carpeta 'dist'")
        print("   2. El ejecutable es autocontenido (no necesita Python instalado)")
        print("   3. Incluye el README.md para instrucciones de uso")
    
    return success

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⏹️ Construcción cancelada por el usuario")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
    finally:
        input("\nPresiona Enter para salir...")

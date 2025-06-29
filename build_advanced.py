#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Constructor Avanzado de Ejecutables para Traductor Endless Sky
Soporta múltiples plataformas y formatos de salida
"""

import os
import sys
import json
import subprocess
import shutil
import platform
from pathlib import Path

class ExecutableBuilder:
    def __init__(self, config_file="build_config.json"):
        self.config = self.load_config(config_file)
        self.platform = platform.system().lower()
        self.current_dir = Path(__file__).parent
        
    def load_config(self, config_file):
        """Carga la configuración desde archivo JSON"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"❌ Archivo de configuración no encontrado: {config_file}")
            return self.get_default_config()
        except json.JSONDecodeError as e:
            print(f"❌ Error en configuración JSON: {e}")
            return self.get_default_config()
    
    def get_default_config(self):
        """Configuración por defecto"""
        return {
            "app": {
                "name": "Traductor Endless Sky",
                "version": "1.0.0",
                "main_script": "run_gui.py"
            },
            "build": {
                "output_dir": "dist",
                "one_file": True,
                "windowed": True
            },
            "includes": ["translator.py", "translator_gui.py"],
            "hidden_imports": ["tkinter", "googletrans"]
        }
    
    def check_dependencies(self):
        """Verifica que las dependencias estén instaladas"""
        print("🔍 Verificando dependencias...")
        
        # Verificar Python
        if sys.version_info < (3, 6):
            print("❌ Se requiere Python 3.6 o superior")
            return False
        
        print(f"✅ Python {sys.version.split()[0]} encontrado")
        
        # Verificar e instalar PyInstaller
        try:
            import PyInstaller
            print("✅ PyInstaller disponible")
        except ImportError:
            print("📦 Instalando PyInstaller...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        
        # Verificar archivos principales
        main_script = self.config["app"]["main_script"]
        if not os.path.exists(main_script):
            print(f"❌ Archivo principal no encontrado: {main_script}")
            return False
        
        print(f"✅ Archivo principal encontrado: {main_script}")
        return True
    
    def create_icon(self):
        """Crea un ícono para la aplicación"""
        icon_path = "icon.ico"
        
        if os.path.exists(icon_path):
            print(f"✅ Ícono existente encontrado: {icon_path}")
            return icon_path
        
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            print("🎨 Creando ícono...")
            size = 256
            img = Image.new('RGBA', (size, size), (0, 120, 215, 255))
            draw = ImageDraw.Draw(img)
            
            # Marco
            margin = 30
            draw.rectangle([margin, margin, size-margin, size-margin], 
                          fill=(255, 255, 255, 255), outline=(0, 0, 0, 255), width=4)
            
            # Texto
            text = "ES"
            try:
                font = ImageFont.truetype("arial.ttf", 80)
            except:
                font = ImageFont.load_default()
            
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            x = (size - text_width) // 2
            y = (size - text_height) // 2 - 10
            
            draw.text((x, y), text, fill=(0, 120, 215, 255), font=font)
            
            # Subtexto
            subtext = "Traductor"
            try:
                subfont = ImageFont.truetype("arial.ttf", 24)
            except:
                subfont = ImageFont.load_default()
            
            bbox = draw.textbbox((0, 0), subtext, font=subfont)
            sub_width = bbox[2] - bbox[0]
            sub_x = (size - sub_width) // 2
            sub_y = y + text_height + 10
            
            draw.text((sub_x, sub_y), subtext, fill=(0, 120, 215, 255), font=subfont)
            
            # Guardar
            img.save(icon_path, format="ICO", sizes=[(256, 256), (128, 128), (64, 64), (32, 32), (16, 16)])
            print(f"✅ Ícono creado: {icon_path}")
            return icon_path
            
        except ImportError:
            print("⚠️ Pillow no disponible, usando ícono por defecto")
            return None
        except Exception as e:
            print(f"⚠️ Error creando ícono: {e}")
            return None
    
    def build_pyinstaller_command(self):
        """Construye el comando de PyInstaller"""
        config = self.config
        app_config = config["app"]
        build_config = config["build"]
        
        cmd = ["pyinstaller"]
        
        # Configuración básica
        if build_config.get("one_file", True):
            cmd.append("--onefile")
        
        if build_config.get("windowed", True):
            cmd.append("--windowed")
        
        if build_config.get("console", False):
            cmd.append("--console")
        
        # Nombre de la aplicación
        cmd.extend(["--name", app_config["name"].replace(" ", "_")])
        
        # Ícono
        icon_path = self.create_icon()
        if icon_path and os.path.exists(icon_path):
            cmd.extend(["--icon", icon_path])
        
        # Directorios
        cmd.extend(["--distpath", build_config.get("output_dir", "dist")])
        cmd.extend(["--workpath", build_config.get("temp_dir", "build")])
        
        # Archivos adicionales
        for include in config.get("includes", []):
            if os.path.exists(include):
                cmd.extend(["--add-data", f"{include};."])
        
        # Imports ocultos
        for hidden_import in config.get("hidden_imports", []):
            cmd.extend(["--hidden-import", hidden_import])
        
        # Exclusiones
        for exclude in config.get("exclude_modules", []):
            cmd.extend(["--exclude-module", exclude])
        
        # UPX
        if build_config.get("upx", True):
            cmd.append("--upx-dir")
            cmd.append(".")
        
        # Argumentos específicos de plataforma
        platform_config = config.get("platforms", {}).get(self.platform, {})
        if platform_config.get("enabled", True):
            additional_args = platform_config.get("additional_args", [])
            cmd.extend(additional_args)
        
        # Archivo principal
        cmd.append(app_config["main_script"])
        
        return cmd
    
    def build_executable(self):
        """Construye el ejecutable"""
        if not self.check_dependencies():
            return False
        
        print(f"\n🚀 Construyendo ejecutable para {self.platform}...")
        
        # Limpiar construcciones anteriores
        build_dir = Path(self.config["build"]["temp_dir"])
        if build_dir.exists():
            shutil.rmtree(build_dir)
        
        # Construir comando
        cmd = self.build_pyinstaller_command()
        
        print(f"🔨 Ejecutando: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.current_dir)
            
            if result.returncode == 0:
                print("✅ Construcción exitosa!")
                
                # Mostrar archivos generados
                dist_dir = Path(self.config["build"]["output_dir"])
                if dist_dir.exists():
                    print("\n📁 Archivos generados:")
                    for file in dist_dir.iterdir():
                        size_mb = file.stat().st_size / (1024 * 1024)
                        print(f"   📄 {file.name} ({size_mb:.1f} MB)")
                
                return True
            else:
                print("❌ Error durante la construcción:")
                print(result.stderr)
                return False
                
        except Exception as e:
            print(f"❌ Error ejecutando PyInstaller: {e}")
            return False
    
    def create_installer(self):
        """Crea un instalador simple"""
        installer_content = f'''@echo off
title Instalador - {self.config["app"]["name"]}

echo ========================================
echo  {self.config["app"]["name"]} v{self.config["app"]["version"]}
echo  Instalador
echo ========================================
echo.

set INSTALL_DIR=%PROGRAMFILES%\\{self.config["app"]["name"].replace(" ", "_")}

echo Creando directorio de instalacion...
mkdir "%INSTALL_DIR%" 2>nul

echo Copiando archivos...
copy "{self.config["app"]["name"].replace(" ", "_")}.exe" "%INSTALL_DIR%\\" >nul

echo Creando acceso directo en el escritorio...
powershell "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('$env:USERPROFILE\\Desktop\\{self.config["app"]["name"]}.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\\{self.config["app"]["name"].replace(" ", "_")}.exe'; $Shortcut.Save()"

echo.
echo ✅ Instalacion completada
echo.
echo El programa esta disponible en:
echo    %INSTALL_DIR%
echo.
echo Acceso directo creado en el escritorio
echo.
pause
'''
        
        installer_path = f"Instalar_{self.config['app']['name'].replace(' ', '_')}.bat"
        with open(installer_path, 'w', encoding='utf-8') as f:
            f.write(installer_content)
        
        print(f"✅ Instalador creado: {installer_path}")
    
    def package_release(self):
        """Empaqueta todo para distribución"""
        print("\n📦 Creando paquete de distribución...")
        
        app_name = self.config["app"]["name"].replace(" ", "_")
        version = self.config["app"]["version"]
        package_name = f"{app_name}_v{version}_{self.platform}"
        
        package_dir = Path(package_name)
        if package_dir.exists():
            shutil.rmtree(package_dir)
        
        package_dir.mkdir()
        
        # Copiar ejecutable
        dist_dir = Path(self.config["build"]["output_dir"])
        for file in dist_dir.glob("*"):
            if file.is_file():
                shutil.copy2(file, package_dir)
        
        # Copiar documentación
        docs = ["README.md", "README_GUI.md"]
        for doc in docs:
            if os.path.exists(doc):
                shutil.copy2(doc, package_dir)
        
        # Crear archivo de versión
        version_info = {
            "app": self.config["app"]["name"],
            "version": self.config["app"]["version"],
            "build_date": str(Path().stat().st_mtime),
            "platform": self.platform,
            "python_version": sys.version
        }
        
        with open(package_dir / "version.json", 'w', encoding='utf-8') as f:
            json.dump(version_info, f, indent=2, ensure_ascii=False)
        
        # Crear instalador si es Windows
        if self.platform == "windows":
            self.create_installer()
            installer_file = f"Instalar_{app_name}.bat"
            if os.path.exists(installer_file):
                shutil.copy2(installer_file, package_dir)
        
        print(f"✅ Paquete creado: {package_dir}")
        return package_dir

def main():
    """Función principal del constructor avanzado"""
    print("🏗️ Constructor Avanzado de Ejecutables")
    print("=" * 50)
    
    builder = ExecutableBuilder()
    
    print(f"🎯 Plataforma detectada: {builder.platform}")
    print(f"📱 Aplicación: {builder.config['app']['name']} v{builder.config['app']['version']}")
    
    print("\n🎮 Opciones de construcción:")
    print("1. Construir ejecutable")
    print("2. Construir y empaquetar")
    print("3. Solo crear configuraciones")
    print("4. Mostrar configuración actual")
    
    try:
        choice = input("\nSelecciona una opción (1-4): ").strip()
        
        if choice == "1":
            success = builder.build_executable()
            if success:
                print("\n🎉 ¡Construcción completada!")
        
        elif choice == "2":
            success = builder.build_executable()
            if success:
                package_dir = builder.package_release()
                print(f"\n🎉 ¡Paquete completo creado en: {package_dir}")
        
        elif choice == "3":
            builder.create_icon()
            builder.create_installer()
            print("✅ Configuraciones creadas")
        
        elif choice == "4":
            print("\n📋 Configuración actual:")
            print(json.dumps(builder.config, indent=2, ensure_ascii=False))
        
        else:
            print("❌ Opción inválida")
    
    except KeyboardInterrupt:
        print("\n⏹️ Construcción cancelada")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")

if __name__ == "__main__":
    main()

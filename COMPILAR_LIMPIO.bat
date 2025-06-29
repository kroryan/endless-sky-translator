@echo off
title Compilador Limpio - Traductor Endless Sky
color 0a
cd /d "%~dp0"

echo ========================================
echo   COMPILADOR LIMPIO Y DIRECTO
echo   Traductor de Endless Sky v2.0
echo ========================================
echo.

echo 🧹 PASO 1: Limpieza total de archivos temporales...
if exist "build" rmdir /s /q "build" 2>nul
if exist "dist" rmdir /s /q "dist" 2>nul
if exist "__pycache__" rmdir /s /q "__pycache__" 2>nul
if exist "*.spec" del /q "*.spec" 2>nul
echo ✅ Limpieza completada

echo.
echo 🔧 PASO 2: Compilación directa con PyInstaller...
echo Usando configuración optimizada para evitar conflictos...

pyinstaller --onefile ^
    --windowed ^
    --name "Endless_Sky_Translator" ^
    --add-data "translator.py;." ^
    --add-data "translations.py;." ^
    --add-data "requirements.txt;." ^
    --hidden-import "tkinter" ^
    --hidden-import "tkinter.ttk" ^
    --hidden-import "tkinter.filedialog" ^
    --hidden-import "tkinter.messagebox" ^
    --hidden-import "tkinter.scrolledtext" ^
    --hidden-import "googletrans" ^
    --hidden-import "googletrans.client" ^
    --hidden-import "googletrans.constants" ^
    --hidden-import "deep_translator" ^
    --hidden-import "requests" ^
    --hidden-import "chardet" ^
    --hidden-import "json" ^
    --hidden-import "threading" ^
    --hidden-import "queue" ^
    --hidden-import "pathlib" ^
    --hidden-import "re" ^
    --hidden-import "time" ^
    --hidden-import "os" ^
    --hidden-import "sys" ^
    --exclude-module "anthropic" ^
    --exclude-module "chromadb" ^
    --exclude-module "civagent" ^
    --exclude-module "civrealm" ^
    --exclude-module "datasets" ^
    --exclude-module "fastapi" ^
    --exclude-module "google-genai" ^
    --exclude-module "gpustack" ^
    --exclude-module "huggingface-hub" ^
    --exclude-module "langchain" ^
    --exclude-module "langfuse" ^
    --exclude-module "langsmith" ^
    --exclude-module "llama-cloud" ^
    --exclude-module "llama-index" ^
    --exclude-module "modelscope" ^
    --exclude-module "ollama" ^
    --exclude-module "openai" ^
    --exclude-module "open-webui" ^
    --exclude-module "pinecone" ^
    --exclude-module "qdrant" ^
    --exclude-module "tensorflow" ^
    --exclude-module "unstructured" ^
    --exclude-module "numpy" ^
    --exclude-module "pandas" ^
    --exclude-module "matplotlib" ^
    --exclude-module "scipy" ^
    --exclude-module "sklearn" ^
    --exclude-module "torch" ^
    --exclude-module "transformers" ^
    --distpath "dist" ^
    --workpath "build" ^
    run_gui.py

if %errorlevel% neq 0 (
    echo.
    echo ❌ Error durante la compilación
    echo 💡 Intentando compilación simplificada...
    echo.
    
    pyinstaller --onefile ^
        --windowed ^
        --name "Endless_Sky_Translator_Simple" ^
        --distpath "dist" ^
        --workpath "build" ^
        run_gui.py
)

echo.
if exist "dist\Endless_Sky_Translator.exe" (
    echo ✅ ¡COMPILACIÓN EXITOSA!
    echo.
    echo 📁 Ejecutable creado: dist\Endless_Sky_Translator.exe
    echo 📏 Tamaño del archivo:
    dir "dist\Endless_Sky_Translator.exe" | findstr /C:"Endless_Sky_Translator.exe"
    echo.
    echo 💡 El ejecutable es completamente independiente
    echo 💡 No necesita Python instalado en otras máquinas
    echo.
    echo 🎮 Para distribuir:
    echo    1. Copia dist\Endless_Sky_Translator.exe
    echo    2. Incluye README_EN.md para instrucciones
    echo    3. ¡Listo para usar!
) else if exist "dist\Endless_Sky_Translator_Simple.exe" (
    echo ✅ ¡COMPILACIÓN SIMPLE EXITOSA!
    echo.
    echo 📁 Ejecutable creado: dist\Endless_Sky_Translator_Simple.exe
    echo 📏 Tamaño del archivo:
    dir "dist\Endless_Sky_Translator_Simple.exe" | findstr /C:"Endless_Sky_Translator_Simple.exe"
) else (
    echo ❌ La compilación falló
    echo.
    echo 🔍 Verifica que PyInstaller esté instalado:
    echo    pip list | findstr pyinstaller
    echo.
    echo 🔍 Verifica que los archivos principales existan:
    echo    - run_gui.py
    echo    - translator.py
    echo    - translations.py
)

echo.
echo 🧹 PASO 3: Limpieza de archivos temporales...
if exist "build" rmdir /s /q "build" 2>nul
if exist "*.spec" del /q "*.spec" 2>nul
echo ✅ Limpieza completada

echo.
echo ========================================
echo          PROCESO COMPLETADO
echo ========================================
pause

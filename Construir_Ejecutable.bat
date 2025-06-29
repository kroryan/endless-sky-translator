@echo off
title Construir Ejecutable - Traductor Endless Sky
color 0a

echo.
echo ========================================
echo   Traductor de Endless Sky
echo   Constructor de Ejecutable v1.0
echo ========================================
echo.

echo 🔍 Verificando Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python no esta instalado o no esta en el PATH
    echo.
    echo 💡 Solucion:
    echo    1. Descarga Python desde https://python.org
    echo    2. Durante la instalacion, marca "Add Python to PATH"
    echo    3. Reinicia esta ventana
    echo.
    pause
    exit /b 1
)

echo ✅ Python detectado correctamente
echo.

echo 📦 Instalando dependencias...
python -m pip install --upgrade pip --quiet
python -m pip install -r requirements.txt --quiet

if %errorlevel% neq 0 (
    echo ❌ Error instalando dependencias
    echo 💡 Intenta ejecutar manualmente: pip install -r requirements.txt
    pause
    exit /b 1
)

echo ✅ Dependencias instaladas
echo.

echo 🏗️ Construyendo ejecutable...
python build_exe.py

echo.
echo ✅ Proceso completado
echo.
echo 📁 Si la construccion fue exitosa, busca el archivo .exe en la carpeta 'dist'
echo.
pause

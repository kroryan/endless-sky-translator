@echo off
title Traductor Endless Sky - Launcher Universal
color 0b

:menu
cls
echo.
echo ████████████████████████████████████████████████
echo   TRADUCTOR DE ENDLESS SKY - LAUNCHER v2.0
echo ████████████████████████████████████████████████
echo.
echo 🎮 Selecciona una opcion:
echo.
echo 1. 🚀 Ejecutar Traductor (GUI)
echo 2. 🏗️ Compilar a Ejecutable (.exe)
echo 3. 📦 Compilar y Empaquetar
echo 4. 🔧 Instalar/Actualizar Dependencias
echo 5. 📋 Ver Informacion del Sistema
echo 6. 🧹 Limpiar Archivos Temporales  
echo 7. ❓ Ayuda y Documentacion
echo 8. ❌ Salir
echo.
set /p choice="Tu eleccion (1-8): "

if "%choice%"=="1" goto run_gui
if "%choice%"=="2" goto build_exe
if "%choice%"=="3" goto build_package
if "%choice%"=="4" goto install_deps
if "%choice%"=="5" goto system_info
if "%choice%"=="6" goto cleanup
if "%choice%"=="7" goto help
if "%choice%"=="8" goto exit
goto menu

:run_gui
echo.
echo 🚀 Ejecutando Traductor GUI...
python run_gui.py
if %errorlevel% neq 0 (
    echo.
    echo ❌ Error ejecutando el traductor
    echo 💡 Prueba instalar dependencias primero (opcion 4)
    pause
)
goto menu

:build_exe
echo.
echo 🏗️ Compilando a ejecutable...
echo.
if exist "build_advanced.py" (
    python build_advanced.py
) else if exist "Construir_Ejecutable.bat" (
    call Construir_Ejecutable.bat
) else (
    echo ❌ No se encontraron scripts de compilacion
    echo 💡 Asegurate de tener todos los archivos
)
pause
goto menu

:build_package
echo.
echo 📦 Compilando y empaquetando...
echo.
if exist "build_advanced.py" (
    echo Usando constructor avanzado...
    python build_advanced.py
) else (
    echo Usando metodo basico...
    python build_exe.py
)
pause
goto menu

:install_deps
echo.
echo 📦 Instalando/Actualizando dependencias...
echo.
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
echo.
if %errorlevel% eq 0 (
    echo ✅ Dependencias instaladas correctamente
) else (
    echo ❌ Error instalando dependencias
    echo 💡 Verifica tu conexion a internet
)
pause
goto menu

:system_info
echo.
echo 📋 INFORMACION DEL SISTEMA
echo ================================
echo.
echo 🐍 Version de Python:
python --version
echo.
echo 📦 Pip version:
python -m pip --version
echo.
echo 💻 Sistema operativo:
systeminfo | findstr /B /C:"OS Name"
echo.
echo 📁 Directorio actual:
echo %cd%
echo.
echo 📄 Archivos del traductor:
if exist "run_gui.py" echo ✅ run_gui.py
if exist "translator.py" echo ✅ translator.py  
if exist "translator_gui.py" echo ✅ translator_gui.py
if exist "requirements.txt" echo ✅ requirements.txt
if not exist "run_gui.py" echo ❌ run_gui.py NO ENCONTRADO
echo.
echo 🔍 Dependencias instaladas:
python -c "import sys; print('✅ Python OK')" 2>nul || echo "❌ Python ERROR"
python -c "import tkinter; print('✅ tkinter OK')" 2>nul || echo "❌ tkinter ERROR"
python -c "import googletrans; print('✅ googletrans OK')" 2>nul || echo "❌ googletrans ERROR"
python -c "import requests; print('✅ requests OK')" 2>nul || echo "❌ requests ERROR"
pause
goto menu

:cleanup
echo.
echo 🧹 Limpiando archivos temporales...
echo.
if exist "build" (
    rmdir /s /q "build"
    echo ✅ Carpeta 'build' eliminada
)
if exist "__pycache__" (
    rmdir /s /q "__pycache__"
    echo ✅ Carpeta '__pycache__' eliminada
)
if exist "*.pyc" (
    del /q "*.pyc"
    echo ✅ Archivos .pyc eliminados
)
if exist "*.spec" (
    del /q "*.spec"
    echo ✅ Archivos .spec eliminados
)
echo.
echo ✅ Limpieza completada
pause
goto menu

:help
echo.
echo ❓ AYUDA Y DOCUMENTACION
echo ========================
echo.
echo 📖 Documentos disponibles:
if exist "README.md" echo   ✅ README.md - Documentacion principal
if exist "BUILD_GUIDE.md" echo   ✅ BUILD_GUIDE.md - Guia de compilacion
if exist "README_GUI.md" echo   ✅ README_GUI.md - Guia de la interfaz
echo.
echo 🆘 SOLUCION DE PROBLEMAS:
echo.
echo ❓ "ModuleNotFoundError":
echo    💡 Ejecuta opcion 4 (Instalar dependencias)
echo.
echo ❓ "No se puede ejecutar Python":
echo    💡 Instala Python desde python.org
echo    💡 Asegurate de marcar "Add to PATH"
echo.
echo ❓ "Error de traduccion":
echo    💡 Verifica conexion a internet
echo    💡 Verifica ruta de Endless Sky
echo.
echo ❓ "Ejecutable muy grande":
echo    💡 Es normal, incluye Python completo
echo    💡 Tamaño tipico: 25-40 MB
echo.
echo 🌐 ENLACES UTILES:
echo    • Python: https://python.org
echo    • Endless Sky: https://endless-sky.github.io
echo    • Documentacion: README.md
echo.
pause
goto menu

:exit
echo.
echo 👋 ¡Gracias por usar el Traductor de Endless Sky!
echo.
echo 🎮 Recuerda:
echo   • El ejecutable estara en la carpeta 'dist/'
echo   • No necesita Python en otras computadoras
echo   • Incluye toda la funcionalidad de la GUI
echo.
echo ¡Que disfrutes traduciendo Endless Sky! 🚀
echo.
timeout /t 3 >nul
exit /b 0

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lanzador para la GUI Mejorada del Traductor de Endless Sky
"""

import sys
import os

# Añadir el directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from translator_gui import main
    
    if __name__ == "__main__":
        print("🚀 Starting Endless Sky Translator - Enhanced Multilingual GUI")
        print("✨ Features: Real checkboxes, smart filtering, safe selection, multilingual interface")
        main()
        
except ImportError as e:
    print(f"❌ Error al importar módulos: {e}")
    print("💡 Asegúrate de que todos los archivos estén en el mismo directorio")
    input("Presiona Enter para salir...")
except Exception as e:
    print(f"❌ Error inesperado: {e}")
    input("Presiona Enter para salir...")

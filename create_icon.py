#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para extraer el ícono de Endless Sky y crear uno para nuestro traductor
"""

import os
import sys
from pathlib import Path

def extract_endless_sky_icon():
    """Extrae el ícono de Endless Sky.exe"""
    
    print("🎨 Extrayendo ícono de Endless Sky...")
    
    # Buscar el ejecutable de Endless Sky
    current_dir = Path(__file__).parent
    endless_sky_exe = current_dir.parent / "Endless Sky.exe"
    
    if not endless_sky_exe.exists():
        print(f"❌ No se encontró Endless Sky.exe en: {endless_sky_exe}")
        return create_fallback_icon()
    
    try:
        # Intentar con Pillow para extraer ícono
        from PIL import Image
        import win32api
        import win32gui
        import win32con
        
        # Extraer ícono usando win32api
        large, small = win32gui.ExtractIconEx(str(endless_sky_exe), 0)
        if large:
            win32gui.DestroyIcon(large[0])
        if small:
            win32gui.DestroyIcon(small[0])
            
        print("✅ Ícono extraído de Endless Sky")
        return True
        
    except ImportError:
        print("⚠️ win32api/PIL no disponible, creando ícono personalizado...")
        return create_custom_endless_sky_icon()
    
    except Exception as e:
        print(f"⚠️ Error extrayendo ícono: {e}")
        return create_custom_endless_sky_icon()

def create_custom_endless_sky_icon():
    """Crea un ícono personalizado inspirado en Endless Sky"""
    
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        print("🎨 Creando ícono personalizado para el traductor...")
        
        # Crear imagen de 256x256 con fondo espacial
        size = 256
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))  # Fondo transparente
        draw = ImageDraw.Draw(img)
        
        # Fondo degradado espacial (azul oscuro a negro)
        for y in range(size):
            alpha = int(255 * (1 - y / size))
            color = (0, 30, 60, alpha)
            draw.line([(0, y), (size, y)], fill=color)
        
        # Dibujar "nave espacial" simplificada
        # Cuerpo principal de la nave
        nave_points = [
            (size//2, size//4),      # Punta superior
            (size//2 + 40, size//2), # Lado derecho
            (size//2 + 30, size*3//4), # Parte trasera derecha
            (size//2 - 30, size*3//4), # Parte trasera izquierda
            (size//2 - 40, size//2), # Lado izquierdo
        ]
        draw.polygon(nave_points, fill=(180, 180, 220, 255), outline=(255, 255, 255, 255), width=2)
        
        # Agregar ventana/cockpit
        cockpit_center = (size//2, size//2 - 20)
        draw.ellipse([cockpit_center[0]-15, cockpit_center[1]-10, 
                     cockpit_center[0]+15, cockpit_center[1]+10], 
                     fill=(100, 150, 255, 200))
        
        # Agregar estrellas de fondo
        import random
        random.seed(42)  # Para consistencia
        for _ in range(20):
            x = random.randint(10, size-10)
            y = random.randint(10, size-10)
            # Evitar área de la nave
            if not (size//2 - 50 < x < size//2 + 50 and size//4 < y < size*3//4):
                draw.ellipse([x-1, y-1, x+1, y+1], fill=(255, 255, 255, 200))
        
        # Texto indicativo
        try:
            # Intentar cargar fuente del sistema
            font = ImageFont.truetype("arial.ttf", 24)
        except:
            font = ImageFont.load_default()
        
        # Texto "TR" (Traductor)
        text = "TR"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        text_x = size//2 - text_width//2
        text_y = size - 50
        
        # Sombra del texto
        draw.text((text_x+2, text_y+2), text, fill=(0, 0, 0, 128), font=font)
        # Texto principal
        draw.text((text_x, text_y), text, fill=(255, 255, 255, 255), font=font)
        
        # Guardar como ICO con múltiples tamaños
        icon_path = "endless_sky_translator.ico"
        img.save(icon_path, format="ICO", sizes=[(256, 256), (128, 128), (64, 64), (32, 32), (16, 16)])
        
        print(f"✅ Ícono personalizado creado: {icon_path}")
        return icon_path
        
    except Exception as e:
        print(f"⚠️ Error creando ícono personalizado: {e}")
        return create_fallback_icon()

def create_fallback_icon():
    """Crea un ícono básico como respaldo"""
    
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        print("🎨 Creando ícono básico...")
        
        size = 256
        img = Image.new('RGBA', (size, size), (0, 120, 215, 255))  # Azul
        draw = ImageDraw.Draw(img)
        
        # Marco
        margin = 20
        draw.rectangle([margin, margin, size-margin, size-margin], 
                      fill=(255, 255, 255, 255), outline=(0, 0, 0, 255), width=4)
        
        # Texto
        text = "ES\nTR"
        try:
            font = ImageFont.truetype("arial.ttf", 48)
        except:
            font = ImageFont.load_default()
        
        lines = text.split('\n')
        total_height = len(lines) * 60
        start_y = (size - total_height) // 2
        
        for i, line in enumerate(lines):
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]
            x = (size - text_width) // 2
            y = start_y + i * 60
            draw.text((x, y), line, fill=(0, 120, 215, 255), font=font)
        
        # Guardar
        icon_path = "translator_icon.ico"
        img.save(icon_path, format="ICO", sizes=[(256, 256), (128, 128), (64, 64), (32, 32), (16, 16)])
        
        print(f"✅ Ícono básico creado: {icon_path}")
        return icon_path
        
    except Exception as e:
        print(f"❌ Error creando ícono básico: {e}")
        return None

if __name__ == "__main__":
    try:
        icon_file = extract_endless_sky_icon()
        if not icon_file:
            icon_file = create_custom_endless_sky_icon()
        if not icon_file:
            icon_file = create_fallback_icon()
            
        if icon_file:
            print(f"🎉 Ícono listo: {icon_file}")
        else:
            print("❌ No se pudo crear ningún ícono")
            
    except Exception as e:
        print(f"❌ Error general: {e}")
        input("Presiona Enter para continuar...")

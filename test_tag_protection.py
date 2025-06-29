#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to verify that <> tag protection works correctly
"""

import sys
import os
from pathlib import Path

# Add the translator directory to the path
sys.path.append(str(Path(__file__).parent))

from translator import EndlessSkyTranslatorFixed

def test_tag_protection():
    """Test that <> tags are preserved during translation"""
    print("🧪 Probando protección de etiquetas <>...")
    
    # Create translator instance
    base_path = r"d:\Program Files (x86)\Steam\steamapps\common\Endless Sky"
    translator = EndlessSkyTranslatorFixed(base_path, 'es')
    
    # Test cases with <> tags
    test_cases = [
        "Bring Amy and Nolan to <destination>, where they will be safe.",
        "You have <tons> tons of cargo on your ship.",
        "Travel to <planet> and meet the contact there.",
        "The <origin> system is under attack.",
        "Your ship has <credits> credits available.",
        "Go to <destination> and deliver the <cargo>.",
        "The mission requires you to go to <system> first."
    ]
    
    print("\n📋 Casos de prueba:")
    for i, test_text in enumerate(test_cases, 1):
        print(f"\n--- Caso {i} ---")
        print(f"📝 Original: {test_text}")
        
        # Translate
        result = translator.translate_text(test_text)
        print(f"✅ Traducido: {result}")
        
        # Verify tags are preserved
        import re
        original_tags = re.findall(r'<[^>]+>', test_text)
        result_tags = re.findall(r'<[^>]+>', result)
        
        if original_tags == result_tags:
            print(f"✅ ÉXITO: Todas las etiquetas preservadas: {original_tags}")
        else:
            print(f"❌ ERROR: Etiquetas no preservadas")
            print(f"   Original: {original_tags}")
            print(f"   Resultado: {result_tags}")
    
    print("\n🎯 Prueba completa!")

if __name__ == "__main__":
    test_tag_protection()

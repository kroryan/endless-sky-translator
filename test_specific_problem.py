#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script specific for the problem mentioned: <destination> being translated
"""

import sys
import os
from pathlib import Path

# Add the translator directory to the path
sys.path.append(str(Path(__file__).parent))

from translator import EndlessSkyTranslatorFixed

def test_specific_problem():
    """Test the specific problem: 'Bring Amy and Nolan to <destination>' being translated incorrectly"""
    print("🎯 Probando el problema específico mencionado...")
    
    # Create translator instance
    base_path = r"d:\Program Files (x86)\Steam\steamapps\common\Endless Sky"
    translator = EndlessSkyTranslatorFixed(base_path, 'es')
    
    # The exact text from the problem report
    problem_text = "Bring Amy and Nolan to <destination>, where they w..."
    
    print(f"\n📝 Texto problema: {problem_text}")
    print("🔧 Aplicando traducción con protección mejorada...")
    
    # Translate with improved protection
    result = translator.translate_text(problem_text)
    
    print(f"✅ Resultado: {result}")
    
    # Verify <destination> is preserved
    if "<destination>" in result:
        print("✅ ÉXITO: La etiqueta <destination> se preservó correctamente")
        print("🎯 El problema ha sido solucionado!")
    else:
        print("❌ ERROR: La etiqueta <destination> no se preservó")
        print("🔧 Se necesita más trabajo...")
    
    # Test a few more similar cases
    print("\n📋 Probando casos similares:")
    similar_cases = [
        "Take the passengers to <destination> safely",
        "Deliver cargo to <planet> in the <system> system", 
        "You need <credits> credits to buy this",
        "The <origin> fleet is approaching"
    ]
    
    for case in similar_cases:
        result = translator.translate_text(case)
        import re
        original_tags = re.findall(r'<[^>]+>', case)
        result_tags = re.findall(r'<[^>]+>', result)
        
        status = "✅" if original_tags == result_tags else "❌"
        print(f"{status} '{case}' -> '{result}'")
    
    print("\n🎯 Verificación completa!")

if __name__ == "__main__":
    test_specific_problem()

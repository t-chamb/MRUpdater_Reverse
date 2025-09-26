#!/usr/bin/env python3
"""
Test script to validate MRUpdater imports
Tests the main application imports to identify missing modules and syntax errors
"""

import sys
import traceback
from pathlib import Path

def test_import(module_name, description=""):
    """Test importing a module and report results"""
    try:
        __import__(module_name)
        print(f"✓ {module_name} - {description}")
        return True
    except ImportError as e:
        print(f"✗ {module_name} - Import Error: {e}")
        return False
    except SyntaxError as e:
        print(f"⚠ {module_name} - Syntax Error: {e}")
        return False
    except Exception as e:
        print(f"⚠ {module_name} - Unexpected Error: {e}")
        return False

def main():
    """Test critical imports for MRUpdater"""
    print("Testing MRUpdater Critical Imports")
    print("=" * 50)
    
    # Test third-party dependencies
    print("\n1. Third-Party Dependencies:")
    third_party_tests = [
        ("PySide6.QtCore", "Qt Core functionality"),
        ("PySide6.QtWidgets", "Qt Widgets"),
        ("PySide6.QtGui", "Qt GUI components"),
        ("serial", "Serial communication"),
        ("usb.core", "USB device access"),
        ("statemachine", "State machine implementation"),
        ("esptool", "ESP32 flashing tool"),
        ("boto3", "AWS S3 integration"),
        ("botocore", "AWS core functionality"),
        ("pydantic", "Data validation"),
        ("platformdirs", "Platform directories"),
        ("reedsolo", "Reed-Solomon error correction"),
    ]
    
    success_count = 0
    for module, desc in third_party_tests:
        if test_import(module, desc):
            success_count += 1
    
    print(f"\nThird-party dependencies: {success_count}/{len(third_party_tests)} successful")
    
    # Test local modules (these may have syntax errors from decompilation)
    print("\n2. Local Project Modules:")
    local_tests = [
        ("config", "Application configuration"),
        ("cartclinic", "Cart Clinic main module"),
        ("flashing_tool", "Flashing tool main module"),
        ("libpyretro", "LibPyRetro main module"),
    ]
    
    local_success = 0
    for module, desc in local_tests:
        if test_import(module, desc):
            local_success += 1
    
    print(f"\nLocal modules: {local_success}/{len(local_tests)} successful")
    
    # Test main application import (this will likely fail due to incomplete decompilation)
    print("\n3. Main Application:")
    try:
        # Try to import main without executing it
        import main
        print("✓ main.py - Main application module imported successfully")
        main_success = True
    except Exception as e:
        print(f"✗ main.py - Failed to import: {e}")
        main_success = False
    
    # Summary
    print("\n" + "=" * 50)
    print("SUMMARY:")
    print(f"Third-party dependencies: {success_count}/{len(third_party_tests)}")
    print(f"Local modules: {local_success}/{len(local_tests)}")
    print(f"Main application: {'✓' if main_success else '✗'}")
    
    total_tests = len(third_party_tests) + len(local_tests) + 1
    total_success = success_count + local_success + (1 if main_success else 0)
    
    print(f"Overall: {total_success}/{total_tests} ({total_success/total_tests*100:.1f}%)")
    
    if total_success == total_tests:
        print("\n🎉 All imports successful! MRUpdater is ready to run.")
        return 0
    else:
        print(f"\n⚠️  {total_tests - total_success} imports failed. See errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
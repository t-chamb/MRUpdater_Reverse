#!/bin/bash
# Activation script for MRUpdater virtual environment

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Activate the virtual environment
source "$SCRIPT_DIR/venv/bin/activate"

echo "MRUpdater virtual environment activated!"
echo "Python version: $(python --version)"
echo "Virtual environment: $VIRTUAL_ENV"

# Test basic imports
echo ""
echo "Testing critical imports..."
python -c "
try:
    import PySide6
    print('✓ PySide6 imported successfully')
except ImportError as e:
    print('✗ PySide6 import failed:', e)

try:
    import serial
    print('✓ pyserial imported successfully')
except ImportError as e:
    print('✗ pyserial import failed:', e)

try:
    import usb
    print('✓ pyusb imported successfully')
except ImportError as e:
    print('✗ pyusb import failed:', e)

try:
    import statemachine
    print('✓ python-statemachine imported successfully')
except ImportError as e:
    print('✗ python-statemachine import failed:', e)

try:
    import esptool
    print('✓ esptool imported successfully')
except ImportError as e:
    print('✗ esptool import failed:', e)

try:
    import boto3
    print('✓ boto3 imported successfully')
except ImportError as e:
    print('✗ boto3 import failed:', e)

try:
    import pydantic
    print('✓ pydantic imported successfully')
except ImportError as e:
    print('✗ pydantic import failed:', e)
"

echo ""
echo "To run the dependency checker:"
echo "python check_dependencies.py --project-root ."
echo ""
echo "To install missing dependencies:"
echo "python check_dependencies.py --project-root . --install"
echo ""
echo "To deactivate the virtual environment, run: deactivate"
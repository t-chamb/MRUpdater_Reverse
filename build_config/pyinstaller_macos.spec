# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec file for MRUpdater macOS application

import os
import sys
from pathlib import Path

# Get the project root directory
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import version information
try:
    from config import __version__, __version_sha__
except ImportError:
    __version__ = "1.0.0"
    __version_sha__ = "unknown"

block_cipher = None

# Define application metadata
APP_NAME = "MRUpdater"
APP_VERSION = __version__
APP_BUNDLE_ID = "com.modretro.mrupdater"
APP_COPYRIGHT = "Copyright © 2024 ModRetro. All rights reserved."

# Define paths
main_script = str(project_root / "main.py")
icon_path = str(project_root / "resources" / "icon.icns") if (project_root / "resources" / "icon.icns").exists() else None

# Data files to include
datas = [
    # Configuration files
    (str(project_root / "config.py"), "."),
    
    # Resources (if they exist)
    (str(project_root / "resources"), "resources") if (project_root / "resources").exists() else None,
    
    # Documentation
    (str(project_root / "README.md"), "."),
    (str(project_root / "LICENSE"), ".") if (project_root / "LICENSE").exists() else None,
    
    # External tools (if present)
    (str(project_root / "tools"), "tools") if (project_root / "tools").exists() else None,
]

# Filter out None entries
datas = [item for item in datas if item is not None]

# Hidden imports - modules that PyInstaller might miss
hiddenimports = [
    # PySide6 modules
    'PySide6.QtCore',
    'PySide6.QtGui', 
    'PySide6.QtWidgets',
    'PySide6.QtNetwork',
    'PySide6.QtSerialPort',
    
    # USB and serial communication
    'usb',
    'usb.core',
    'usb.util',
    'serial',
    'serial.tools',
    'serial.tools.list_ports',
    
    # AWS/S3 for firmware downloads
    'boto3',
    'botocore',
    'botocore.config',
    
    # Cryptography
    'cryptography',
    'cryptography.fernet',
    
    # Data validation
    'pydantic',
    'pydantic.dataclasses',
    
    # State machine
    'statemachine',
    
    # System monitoring
    'psutil',
    
    # Application modules
    'cartclinic',
    'cartclinic.gui',
    'cartclinic.cartridge_read',
    'cartclinic.cartridge_write',
    'cartclinic.mrpatcher',
    'cartclinic.save_to_rom',
    'cartclinic.exceptions',
    'cartclinic.consts',
    
    'flashing_tool',
    'flashing_tool.chromatic',
    'flashing_tool.firmware_flasher',
    'flashing_tool.fpga_flasher',
    'flashing_tool.mcu_flasher',
    'flashing_tool.device_manager',
    'flashing_tool.macos_usb',
    'flashing_tool.macos_binaries',
    
    'libpyretro',
    'libpyretro.cartclinic',
    'libpyretro.cartclinic.comms',
    'libpyretro.cartclinic.protocol',
    'libpyretro.feature_api',
    
    # Performance optimization
    'performance_optimization',
    
    # Progress reporting
    'progress_reporting',
    
    # Error handling
    'exceptions',
    'error_dialog',
    'error_recovery',
    
    # Logging
    'logging_config',
    'logging_init',
]

# Binaries to include (external executables)
binaries = []

# Add macOS-specific binaries if they exist
macos_tools = [
    'openFPGALoader',
    'esptool',
    'esptool.py'
]

for tool in macos_tools:
    tool_path = project_root / "tools" / "macos" / tool
    if tool_path.exists():
        binaries.append((str(tool_path), "tools/macos"))

# Exclude unnecessary modules to reduce bundle size
excludes = [
    # Development tools
    'pytest',
    'unittest',
    'doctest',
    'pdb',
    'pydoc',
    
    # Unused GUI frameworks
    'tkinter',
    'PyQt5',
    'PyQt6',
    
    # Unused libraries
    'matplotlib',
    'numpy',
    'scipy',
    'pandas',
    'jupyter',
    'IPython',
    
    # Documentation tools
    'sphinx',
    'jinja2',
    
    # Build tools
    'setuptools',
    'pip',
    'wheel',
    
    # Testing frameworks
    'nose',
    'coverage',
]

# Analysis step
a = Analysis(
    [main_script],
    pathex=[str(project_root)],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Remove duplicate entries
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# Create executable
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name=APP_NAME,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # GUI application
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

# Create macOS app bundle
app = BUNDLE(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    name=f'{APP_NAME}.app',
    icon=icon_path,
    bundle_identifier=APP_BUNDLE_ID,
    version=APP_VERSION,
    info_plist={
        'CFBundleName': APP_NAME,
        'CFBundleDisplayName': APP_NAME,
        'CFBundleVersion': APP_VERSION,
        'CFBundleShortVersionString': APP_VERSION,
        'CFBundleIdentifier': APP_BUNDLE_ID,
        'CFBundleExecutable': APP_NAME,
        'CFBundlePackageType': 'APPL',
        'CFBundleSignature': '????',
        'NSHumanReadableCopyright': APP_COPYRIGHT,
        'NSHighResolutionCapable': True,
        'LSMinimumSystemVersion': '10.15.0',  # macOS Catalina minimum
        'NSRequiresAquaSystemAppearance': False,  # Support dark mode
        
        # USB device access permissions
        'NSUSBDeviceUsageDescription': 'MRUpdater needs USB access to communicate with Chromatic devices.',
        
        # Network access for firmware downloads
        'NSNetworkUsageDescription': 'MRUpdater needs network access to download firmware updates.',
        
        # File system access
        'NSDocumentsFolderUsageDescription': 'MRUpdater needs access to save ROM files and logs.',
        'NSDownloadsFolderUsageDescription': 'MRUpdater needs access to save downloaded files.',
        
        # Supported file types
        'CFBundleDocumentTypes': [
            {
                'CFBundleTypeName': 'Game Boy ROM',
                'CFBundleTypeExtensions': ['gb', 'gbc'],
                'CFBundleTypeRole': 'Editor',
                'CFBundleTypeIconFile': 'rom_icon.icns',
                'LSHandlerRank': 'Owner',
            },
            {
                'CFBundleTypeName': 'IPS Patch',
                'CFBundleTypeExtensions': ['ips'],
                'CFBundleTypeRole': 'Editor',
                'CFBundleTypeIconFile': 'patch_icon.icns',
                'LSHandlerRank': 'Owner',
            },
        ],
        
        # URL schemes (for future use)
        'CFBundleURLTypes': [
            {
                'CFBundleURLName': 'MRUpdater Protocol',
                'CFBundleURLSchemes': ['mrupdater'],
            }
        ],
        
        # Security settings
        'NSAppTransportSecurity': {
            'NSAllowsArbitraryLoads': False,
            'NSExceptionDomains': {
                # Allow connections to ModRetro servers
                'modretro.com': {
                    'NSExceptionAllowsInsecureHTTPLoads': False,
                    'NSExceptionMinimumTLSVersion': '1.2',
                },
                # Allow connections to AWS S3 for firmware downloads
                'amazonaws.com': {
                    'NSExceptionAllowsInsecureHTTPLoads': False,
                    'NSExceptionMinimumTLSVersion': '1.2',
                },
            }
        },
        
        # Hardware requirements
        'LSRequiresNativeExecution': True,
        
        # Application category
        'LSApplicationCategoryType': 'public.app-category.developer-tools',
    }
)
# MRUpdater Source Code

This repository contains the decompiled and reconstructed source code of ModRetro's MRUpdater application, obtained through reverse engineering of the official distribution packages.

## Overview

MRUpdater is the official tool for updating ModRetro Chromatic handheld gaming devices and managing Game Boy cartridges through the "Cart Clinic" functionality.

## Architecture

The application is built using:
- **Python 3.10** with PyQt/PySide for the GUI
- **PyInstaller** for packaging
- **USB CDC-ACM** serial communication for device interaction

## Module Structure

### Core Modules

- `main.py` - Application entry point
- `flashing_tool/` - Main application framework and device communication
- `cartclinic/` - Cart Clinic functionality for cartridge operations
- `libpyretro/` - Low-level communication library

### Key Components

#### Device Communication (`flashing_tool/`)
- `chromatic.py` - Device detection and management
- `chromatic_subprocess.py` - Subprocess handling for operations
- `constants.py` - Application constants
- `config_parser.py` - Configuration management
- `gui/` - Main GUI components

#### Cart Clinic (`cartclinic/`)
- `cartridge_read.py` - Cartridge reading operations
- `cartridge_write.py` - Cartridge writing operations
- `mrpatcher.py` - ROM patching functionality
- `save_to_rom.py` - Save data management
- `gui.py` - Cart Clinic GUI interface

#### Communication Layer (`libpyretro/`)
- `cartclinic/cart_api.py` - Cartridge API interface
- `cartclinic/comms/` - USB communication protocols
- `feature_api/` - Feature API interface

## USB Communication

The application communicates with the ModRetro Chromatic via:
- **USB VID:PID**: 0x374E:0x013F
- **Protocol**: USB CDC-ACM serial on Endpoint 3
- **Operations**: Cartridge read/write, ROM patching, save management

## Legal Notice

This source code was obtained through legitimate reverse engineering of publicly distributed binaries for interoperability purposes. The decompilation was performed using:
- String extraction and file structure analysis
- No direct code copying from original sources
- Clean-room implementation based on protocol observation

## Usage

This source code is provided for:
- Educational purposes
- Protocol documentation
- Development of compatible tools
- Community research

## Dependencies

Based on the module structure, the application requires:
- PyQt/PySide (GUI framework)
- pyserial (USB communication)
- boto3/botocore (AWS S3 integration)
- esptool (ESP32 communication)
- pydantic (data validation)

## Contributing

This is a research repository. For active development of compatible tools, see the related projects in the ModRetro Chromatic ecosystem.

## Disclaimer

This repository is not affiliated with ModRetro. It is an independent reverse engineering effort for interoperability and educational purposes.
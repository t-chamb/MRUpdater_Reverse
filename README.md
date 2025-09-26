# MRUpdater Decompilation Summary

This directory contains the decompiled Python source code from the MRUpdater.exe application. The decompilation was performed using the patched pycdc tool to handle Python 3.10 bytecode.

## Successfully Decompiled Files

### Main Application
- `main.py` - Main entry point and GUI class (558 lines)
  - Contains the main application window and UI logic
  - Manages firmware downloads, updates, and Cart Clinic integration
  - Uses PySide6 for Qt GUI

### Cart Clinic Module (`cartclinic/`)
- `mrpatcher.py` - MRPatcher API client (77 lines)
  - Handles communication with the game patching service
  - Sends game ROMs for patching
- `cc_subprocess.py` - Cart Clinic subprocess management (904 lines)
  - Manages threading and subprocess operations for Cart Clinic
- `gui.py` - Cart Clinic GUI components (653 lines)
  - Cart Clinic specific UI screens and logic
- `cartridge_read.py` - Cartridge reading functionality (48 lines)
- `cartridge_write.py` - Cartridge writing functionality (116 lines)
- `save_to_rom.py` - Save file to ROM operations (126 lines)

### Flashing Tool Module (`flashing_tool/`)
- `chromatic.py` - Chromatic device state machine (451 lines)
  - Manages USB device detection and firmware flashing
  - Contains state machine for update process
- `chromatic_subprocess.py` - Subprocess operations (106 lines) [partially decompiled]
- `config_parser.py` - Configuration file parsing (54 lines)
- `constants.py` - Application constants (17 lines)
  - Contains app name, S3 bucket info, feature flags
- `s3_wrapper.py` - AWS S3 operations (75 lines)
  - Downloads firmware from updates.modretro.com bucket
- `util.py` - Utility functions (89 lines)
- `features/manager.py` - Feature flag management (125 lines)
  - Handles activation codes and feature toggles

### LibPyRetro Module (`libpyretro/`)
- `feature_api/feature_api_client.py` - Feature API client (26 lines)
  - Communicates with feature server
- `cartclinic/cart_api.py` - Cart API protocol (283 lines)
  - Low-level cartridge communication protocol
- `cartclinic/comms/session.py` - Communication session (611 lines) [partially decompiled]
  - Manages serial communication with cartridge

### External Libraries
- `requests/sessions.py` - HTTP session management (497 lines)
- `botocore/session.py` - AWS SDK session (1077 lines)

## Key Findings

1. **Architecture**: The application uses a Qt-based GUI (PySide6) with state machine-driven firmware updates
2. **S3 Integration**: Firmware is downloaded from `updates.modretro.com` S3 bucket
3. **Feature Flags**: Supports preview/rollback firmware via activation codes
4. **Cart Clinic**: Integrated game patching service that communicates with a remote API
5. **Device Communication**: Uses USB for Chromatic device and serial for cartridge operations

## Decompilation Issues

Some files had minor issues:
- Dataclass definitions appear as `<NODE:12>` placeholders
- Some exception handling shows as incomplete
- A few opcode warnings (RERAISE, JUMP_IF_NOT_EXC_MATCH) that were patched

Overall, the decompilation was successful and provides a clear understanding of the MRUpdater application structure and functionality.
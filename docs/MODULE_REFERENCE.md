# MRUpdater Module Reference

## Core Modules

### `main.py`

Application entry point and initialization.

**Key Functions:**

- Application startup and configuration
- GUI initialization
- Error handling setup
- Resource loading

### `flashing_tool/`

Main application framework and device management.

#### `chromatic.py`

Device detection and management for ModRetro Chromatic.

**Key Classes:**

- `Chromatic` - Main device interface
- `ChromaticError` - Device-specific exceptions
- `ChromaticFirmwarePackage` - Firmware management

**Key Functions:**

- Device enumeration and detection
- Connection establishment and management
- Firmware update coordination
- Device status monitoring

#### `chromatic_subprocess.py`

Subprocess management for long-running operations.

**Key Functions:**

- Process spawning and management
- Inter-process communication
- Progress monitoring
- Error handling and cleanup

#### `constants.py`

Application-wide constants and configuration values.

**Key Constants:**

- USB device identifiers (VID:PID)
- Protocol constants
- Application metadata
- Default configuration values

#### `config_parser.py`

Configuration file parsing and management.

**Key Functions:**

- Configuration file loading
- Settings validation
- Default value handling
- Configuration persistence

#### `gui/`

Main application GUI components.

**Key Modules:**

- `alert_dialog.py` - Error and information dialogs
- `changelog_dialog.py` - Version change notifications
- Generated UI files from Qt Designer

#### `features/`

Feature management and capability detection.

**Key Classes:**

- `FeatureManager` - Feature discovery and management
- Feature-specific implementations

#### `plugins/`

Plugin system for extensible functionality.

**Key Modules:**

- `base/` - Base plugin interfaces
- `base/manager.py` - Plugin lifecycle management
- `base/tab.py` - Tab-based plugin architecture

### `cartclinic/`

Cart Clinic functionality for cartridge operations.

#### `gui.py`

Cart Clinic user interface components.

**Key Classes:**

- Cart Clinic main interface
- Progress dialogs
- Operation confirmation dialogs

#### `cartridge_read.py`

Cartridge reading operations.

**Key Functions:**

- ROM data extraction
- Save data reading
- Cartridge header analysis
- Metadata extraction

#### `cartridge_write.py`

Cartridge writing operations.

**Key Functions:**

- ROM flashing
- Save data writing
- Write verification
- Progress reporting

#### `mrpatcher.py`

ROM patching functionality.

**Key Functions:**

- IPS patch application
- Binary ROM modifications
- Patch validation
- Backup management

#### `save_to_rom.py`

Save data management operations.

**Key Functions:**

- Save extraction from cartridge
- Save injection to ROM
- Format conversion
- Data validation

#### `cc_subprocess.py`

Subprocess handling for Cart Clinic operations.

**Key Functions:**

- Operation process management
- Progress monitoring
- Error handling
- Resource cleanup

#### `animation.py`

UI animation effects for Cart Clinic.

**Key Functions:**

- Progress animations
- Status indicators
- Visual feedback effects

#### `consts.py`

Cart Clinic specific constants.

**Key Constants:**

- Cartridge type identifiers
- Operation parameters
- Error codes
- Default settings

#### `exceptions.py`

Cart Clinic error handling.

**Key Classes:**

- `CartClinicError` - Base Cart Clinic exception
- Operation-specific exceptions
- Error recovery mechanisms

### `libpyretro/`

Low-level communication library.

#### `cartclinic/`

Cart Clinic communication protocols.

##### `cart_api.py`

High-level cartridge API interface.

**Key Classes:**

- `CartAPI` - Main API interface
- Command builders and parsers
- Response handlers

**Key Functions:**

- Command construction
- Response parsing
- Error handling
- Session management

##### `comms/`

Low-level USB communication.

**Key Modules:**

- `session.py` - Session management
- `exceptions.py` - Communication exceptions
- Protocol implementation

#### `feature_api/`

Feature API for device capability management.

**Key Functions:**

- Feature discovery
- Capability negotiation
- Version checking
- Status monitoring

#### `ips_util/`

IPS patch utility functions.

**Key Functions:**

- IPS file parsing
- Patch application
- Validation and verification
- Error handling

## Third-Party Modules

### `pydantic/`

Data validation and settings management.

**Key Components:**

- `config.py` - Configuration validation
- `v1/` - Pydantic v1 compatibility
- `_internal/` - Internal utilities

### External Dependencies

#### `six.py`

Python 2/3 compatibility utilities.

#### `reedsolo.py`

Reed-Solomon error correction for data integrity.

## Module Dependencies

```
main.py
├── flashing_tool/
│   ├── chromatic.py
│   ├── gui/
│   └── features/
├── cartclinic/
│   ├── gui.py
│   ├── cartridge_read.py
│   ├── cartridge_write.py
│   └── mrpatcher.py
└── libpyretro/
    ├── cartclinic/cart_api.py
    └── feature_api/
```

## Usage Patterns

### Device Operations

```python
from flashing_tool.chromatic import Chromatic

# Device detection
device = Chromatic.detect()

# Connection management
with device.connect() as conn:
    # Perform operations
    pass
```

### Cart Clinic Operations

```python
from cartclinic.cartridge_read import CartridgeReader
from libpyretro.cartclinic.cart_api import CartAPI

# Initialize API
api = CartAPI(device)

# Read cartridge
reader = CartridgeReader(api)
rom_data = reader.read_rom()
```

### Error Handling

```python
from cartclinic.exceptions import CartClinicError
from libpyretro.cartclinic.comms.exceptions import CommunicationError

try:
    # Perform operation
    pass
except CommunicationError as e:
    # Handle communication failure
    pass
except CartClinicError as e:
    # Handle operation failure
    pass
```

## Development Guidelines

### Adding New Features

1. Define interfaces in appropriate modules
2. Implement business logic
3. Add GUI components
4. Update documentation
5. Add error handling

### Testing

1. Unit tests for individual modules
2. Integration tests for workflows
3. Hardware testing with real devices
4. Error condition testing

### Code Style

1. Follow PEP 8 conventions
2. Use type hints where appropriate
3. Document public interfaces
4. Handle errors gracefully

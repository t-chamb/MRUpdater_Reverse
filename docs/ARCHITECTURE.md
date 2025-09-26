# MRUpdater Architecture

## Overview

MRUpdater is a PyQt-based desktop application for managing ModRetro Chromatic devices and Game Boy cartridges. The application follows a modular architecture with clear separation between GUI, business logic, and communication layers.

## Module Hierarchy

```
MRUpdater/
├── main.py                      # Application entry point
├── flashing_tool/               # Core application framework
│   ├── chromatic.py            # Device management
│   ├── chromatic_subprocess.py # Process handling
│   ├── constants.py            # Application constants
│   ├── config_parser.py        # Configuration management
│   ├── gui/                    # Main GUI components
│   ├── features/               # Feature management
│   └── plugins/                # Plugin system
├── cartclinic/                 # Cart Clinic functionality
│   ├── gui.py                  # Cart Clinic UI
│   ├── cartridge_read.py       # Read operations
│   ├── cartridge_write.py      # Write operations
│   ├── mrpatcher.py            # ROM patching
│   └── save_to_rom.py          # Save management
└── libpyretro/                 # Communication library
    ├── cartclinic/             # Cart Clinic protocols
    │   ├── cart_api.py         # API interface
    │   └── comms/              # USB communication
    └── feature_api/            # Feature API
```

## Communication Flow

1. **GUI Layer** (`flashing_tool/gui/`, `cartclinic/gui.py`)
   - User interface components
   - Event handling and user interactions
   - Progress reporting and status updates

2. **Business Logic** (`cartclinic/`, `flashing_tool/`)
   - Operation orchestration
   - Data validation and processing
   - Error handling and recovery

3. **API Layer** (`libpyretro/`)
   - Protocol abstraction
   - Command formatting and parsing
   - Session management

4. **Communication Layer** (`libpyretro/cartclinic/comms/`)
   - USB serial communication
   - Low-level protocol handling
   - Device detection and management

## Key Components

### Device Management (`flashing_tool/chromatic.py`)
- Device detection via USB VID:PID (0x374E:0x013F)
- Connection management and health monitoring
- Firmware update coordination

### Cart Clinic Operations (`cartclinic/`)
- **Reading**: Extract ROM and save data from cartridges
- **Writing**: Flash new ROM data to cartridges
- **Patching**: Apply IPS patches and modifications
- **Save Management**: Backup and restore save data

### Communication Protocol (`libpyretro/cartclinic/`)
- USB CDC-ACM serial communication on Endpoint 3
- Command/response protocol with timeout handling
- Session management and error recovery

## Data Flow

```
User Action → GUI Event → Business Logic → API Call → USB Command → Device Response → Data Processing → GUI Update
```

## Error Handling

The application implements hierarchical error handling:

1. **Communication Errors** (`libpyretro/cartclinic/comms/exceptions.py`)
   - USB connection failures
   - Protocol timeouts
   - Device communication errors

2. **Operation Errors** (`cartclinic/exceptions.py`)
   - Cartridge read/write failures
   - ROM patching errors
   - Save data corruption

3. **Application Errors** (`flashing_tool/`)
   - Configuration errors
   - Resource loading failures
   - GUI exceptions

## Threading Model

- **Main Thread**: GUI operations and user interactions
- **Worker Threads**: Long-running operations (read/write/patch)
- **Communication Thread**: USB protocol handling
- **Progress Threads**: Status updates and progress reporting

## Configuration Management

Configuration is handled through:
- Application settings (`flashing_tool/config_parser.py`)
- Feature flags (`flashing_tool/features/`)
- User preferences and device settings
- Firmware package management

## Plugin System

The application supports plugins through:
- Base plugin interface (`flashing_tool/plugins/base/`)
- Plugin manager (`flashing_tool/plugins/base/manager.py`)
- Tab-based plugin architecture (`flashing_tool/plugins/base/tab.py`)

## Security Considerations

- USB communication validation
- Firmware signature verification
- Safe ROM patching with backup
- User consent for destructive operations
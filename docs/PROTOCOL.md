# MRUpdater Communication Protocol

## Overview

MRUpdater communicates with the ModRetro Chromatic device using USB CDC-ACM serial communication. The protocol is implemented in the `libpyretro.cartclinic.comms` module.

## USB Communication

### Device Identification
- **USB Vendor ID**: 0x374E
- **USB Product ID**: 0x013F
- **Interface**: USB CDC-ACM (Serial)
- **Endpoint**: Endpoint 3

### Connection Parameters
- **Baud Rate**: Standard USB CDC-ACM (typically 115200)
- **Data Bits**: 8
- **Stop Bits**: 1
- **Parity**: None
- **Flow Control**: None

## Protocol Structure

### Session Management
The communication follows a session-based protocol:

1. **Session Initialization**
   - Device detection and enumeration
   - Capability negotiation
   - Feature discovery

2. **Command/Response Cycle**
   - Command transmission
   - Response waiting with timeout
   - Error handling and retry logic

3. **Session Termination**
   - Cleanup operations
   - Resource release

### Command Format
Based on the module structure, commands likely follow this pattern:

```
[HEADER][COMMAND][LENGTH][DATA][CHECKSUM]
```

- **HEADER**: Protocol identifier
- **COMMAND**: Operation type (read/write/patch/etc.)
- **LENGTH**: Data payload length
- **DATA**: Command-specific payload
- **CHECKSUM**: Data integrity verification

## Cart Clinic Operations

### Cartridge Reading (`cartclinic/cartridge_read.py`)
Operations for extracting data from Game Boy cartridges:

- **ROM Reading**: Extract complete ROM data
- **Save Reading**: Extract save game data
- **Header Analysis**: Read cartridge header information
- **Metadata Extraction**: Get cartridge type, size, etc.

### Cartridge Writing (`cartclinic/cartridge_write.py`)
Operations for writing data to cartridges:

- **ROM Flashing**: Write new ROM data
- **Save Writing**: Restore save game data
- **Verification**: Verify written data integrity
- **Progress Reporting**: Real-time write progress

### ROM Patching (`cartclinic/mrpatcher.py`)
Advanced ROM modification operations:

- **IPS Patch Application**: Apply IPS format patches
- **Binary Modifications**: Direct ROM editing
- **Backup Creation**: Automatic backup before patching
- **Patch Validation**: Verify patch compatibility

### Save Management (`cartclinic/save_to_rom.py`)
Save data operations:

- **Save Extraction**: Extract save data from cartridge
- **Save Injection**: Write save data to ROM
- **Format Conversion**: Handle different save formats
- **Integrity Checking**: Validate save data

## Error Handling

### Communication Errors
- **Connection Timeout**: Device not responding
- **Protocol Error**: Invalid response format
- **Checksum Mismatch**: Data corruption detected
- **Device Busy**: Device in use by another process

### Operation Errors
- **Read Failure**: Cannot read from cartridge
- **Write Failure**: Cannot write to cartridge
- **Verification Error**: Written data doesn't match
- **Cartridge Error**: Hardware or cartridge issue

### Recovery Mechanisms
- **Automatic Retry**: Retry failed operations
- **Graceful Degradation**: Fall back to safe modes
- **User Notification**: Clear error reporting
- **State Recovery**: Restore previous state

## Feature API

The `libpyretro.feature_api` module provides:

- **Feature Discovery**: Enumerate device capabilities
- **Version Checking**: Verify firmware compatibility
- **Capability Negotiation**: Select optimal operation modes
- **Status Monitoring**: Real-time device status

## Security Features

### Data Integrity
- **Checksums**: Verify data transmission integrity
- **Verification**: Compare written data with source
- **Backup**: Automatic backup before modifications

### Safe Operations
- **User Consent**: Confirm destructive operations
- **Progress Monitoring**: Real-time operation status
- **Abort Capability**: Cancel long-running operations
- **Error Recovery**: Handle partial failures safely

## Implementation Notes

### Threading
- Communication operations run in separate threads
- GUI remains responsive during long operations
- Progress updates via thread-safe mechanisms

### Performance
- Optimized read/write operations
- Efficient data transfer protocols
- Minimal overhead for small operations

### Compatibility
- Support for various Game Boy cartridge types
- Backward compatibility with older firmware
- Graceful handling of unsupported features

## Development Guidelines

### Adding New Operations
1. Define operation in appropriate module
2. Implement protocol commands
3. Add error handling
4. Update GUI components
5. Test with real hardware

### Protocol Extensions
1. Maintain backward compatibility
2. Version negotiation for new features
3. Graceful fallback for older devices
4. Comprehensive testing

### Error Handling
1. Specific error types for different failures
2. User-friendly error messages
3. Recovery suggestions
4. Logging for debugging
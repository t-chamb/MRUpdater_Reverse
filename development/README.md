# Development and Testing Files

This directory contains development scripts, test files, and documentation created during the development of the MRUpdater ROM dumping functionality.

## Test Scripts

### ROM Dumping Tests
- `test_raw_protocol.py` - Low-level protocol testing
- `test_protocol_fix.py` - Protocol optimization testing
- `test_cartridge_*.py` - Various cartridge reading tests
- `quick_rom_test.py` - Speed testing for ROM reading
- `rom_dumper.py` - Original slow ROM dumper (superseded by fast_rom_dumper.py)

### Device Detection Tests
- `test_device_detection.py` - Device connection testing
- `test_usb_detection.py` - USB port detection
- `test_hardware_troubleshooting.py` - Hardware diagnostics

### Integration Tests
- `test_cartridge_read_integration.py` - Full integration testing
- `test_cartridge_read_simple.py` - Simple read tests
- `test_real_hardware.py` - Real hardware validation

## Demo Files
- `cartridge_read_demo.py` - Demo script for cartridge reading
- `demo_cartridge_read.py` - Alternative demo implementation
- `demo_cartridge.gb/.txt` - Small demo ROM files
- `small_cart.gb/.txt` - Test cartridge files

## Documentation
- `*SUMMARY.md` - Various development summaries and analysis documents
- Protocol analysis and implementation notes
- Error handling and performance optimization documentation

## Usage

These files are kept for reference and debugging purposes. For production ROM dumping, use the main `fast_rom_dumper.py` script in the parent directory.

## Key Achievements

The development process resulted in:
- 70x speed improvement (from 11 bytes/s to 789 bytes/s)
- 100% accurate ROM dumps
- Fixed banking logic bug
- Optimized USB transport layer
- Production-ready ROM dumper
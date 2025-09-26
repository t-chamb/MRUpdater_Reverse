# MRUpdater Testing Guide

This document provides comprehensive information about testing MRUpdater with real hardware, including test procedures, validation criteria, and troubleshooting.

## Overview

MRUpdater testing involves multiple levels of validation:

1. **Unit Tests**: Individual component testing
2. **Integration Tests**: Component interaction testing  
3. **Hardware Tests**: Real device and cartridge testing
4. **End-to-End Tests**: Complete workflow validation
5. **Performance Tests**: Speed and memory usage validation

## Hardware Test Requirements

### Required Hardware

**Essential Hardware:**
- ModRetro Chromatic device (latest firmware recommended)
- USB cable (high-quality, data-capable)
- macOS computer with USB ports
- Game Boy cartridges for testing (various types recommended)

**Recommended Hardware:**
- Multiple Chromatic devices (for multi-device testing)
- Various cartridge types:
  - Standard Game Boy cartridges (MBC1, MBC3, MBC5)
  - Game Boy Color cartridges
  - Flash cartridges (for write testing)
  - Homebrew cartridges
- USB hub (powered, for connection testing)
- Different USB cables (for connection reliability testing)

### Software Prerequisites

**Required Software:**
- Python 3.8 or later
- MRUpdater source code
- All dependencies from `requirements.txt`

**Optional Software:**
- Game Boy emulator (for ROM validation)
- Hex editor (for ROM analysis)
- USB monitoring tools (for debugging)

## Test Categories

### 1. Device Detection and Communication Tests

**Purpose**: Verify MRUpdater can detect and communicate with Chromatic devices.

**Test Cases:**

#### Device Detection Test
```bash
# Run device detection test
python tests/hardware_validation.py --device-test
```

**Validation Criteria:**
- ✅ Device detected within 30 seconds
- ✅ Correct USB VID:PID (0x374E:0x013F) identified
- ✅ Device serial number retrieved
- ✅ Basic communication established

**Expected Results:**
- Device appears in device list
- Serial number matches device label
- Communication latency < 100ms
- No connection errors

#### Device Communication Test
**Validation Criteria:**
- ✅ Device info retrieval successful
- ✅ Firmware version query successful
- ✅ Device status query successful
- ✅ Ping/response test successful

#### Device Recovery Test
**Validation Criteria:**
- ✅ Device recovers from simulated error states
- ✅ Communication restored after recovery
- ✅ Device remains stable after recovery

### 2. Firmware Flashing Tests

**Purpose**: Validate firmware download, validation, and flashing capabilities.

**Test Cases:**

#### Firmware Download Test
```bash
# Test firmware download
python tests/hardware_validation.py --firmware-test --firmware-version latest
```

**Validation Criteria:**
- ✅ Firmware manifest retrieved successfully
- ✅ Firmware package downloaded completely
- ✅ Package integrity verified (checksums match)
- ✅ Download completes within reasonable time

**Expected Results:**
- Manifest contains valid firmware entries
- Downloaded package size matches manifest
- No network errors or timeouts
- Package contains both MCU and FPGA components

#### Firmware Validation Test
**Validation Criteria:**
- ✅ Compatibility check passes
- ✅ Version comparison works correctly
- ✅ Bootloader compatibility verified
- ✅ No validation errors reported

#### Firmware Flash Preparation Test
**Validation Criteria:**
- ✅ Device enters flash mode successfully
- ✅ All required tools available
- ✅ Flash preparation completes without errors
- ✅ Device remains responsive during preparation

**⚠️ Note**: Actual firmware flashing is not performed in automated tests to avoid potential device damage. Manual firmware flashing should be tested separately with extreme caution.

### 3. Cartridge Operation Tests

**Purpose**: Validate cartridge detection, reading, and writing operations.

**Test Cases:**

#### Cartridge Detection Test
```bash
# Test cartridge detection
python tests/hardware_validation.py --cartridge-test
```

**Validation Criteria:**
- ✅ Cartridge presence detected correctly
- ✅ Cartridge type identified (Game Boy/Game Boy Color)
- ✅ ROM size detected accurately
- ✅ Mapper type identified correctly
- ✅ Save type detected (if applicable)

**Expected Results:**
- Cartridge info matches known cartridge specifications
- Detection works with various cartridge types
- No false positives or negatives

#### Cartridge Read Test
**Validation Criteria:**
- ✅ ROM data read completely
- ✅ Read speed within acceptable range (>10 KB/s)
- ✅ Header checksum validates correctly
- ✅ No data corruption detected
- ✅ Multiple reads produce identical results

**Expected Results:**
- ROM size matches cartridge specifications
- Header information is valid
- Checksum calculations are correct
- Read operation completes without errors

#### Cartridge Write Test (Optional)
```bash
# Test cartridge writing (requires writable cartridge)
python tests/hardware_validation.py --cartridge-test --rom-path test.gb
```

**⚠️ Warning**: This test will overwrite cartridge data. Only use with test/flash cartridges.

**Validation Criteria:**
- ✅ ROM data written successfully
- ✅ Write verification passes
- ✅ Written data matches source data
- ✅ Write speed within acceptable range

**Expected Results:**
- Write operation completes without errors
- Verification read matches written data
- Cartridge remains functional after write

### 4. End-to-End Workflow Tests

**Purpose**: Validate complete user workflows from start to finish.

#### Complete Firmware Update Workflow
1. **Device Detection**: Connect and detect Chromatic device
2. **Version Check**: Check current firmware version
3. **Update Check**: Check for available updates
4. **Download**: Download firmware package
5. **Validation**: Validate firmware compatibility
6. **Flash Preparation**: Prepare device for flashing
7. **Progress Monitoring**: Monitor flash progress
8. **Verification**: Verify successful flash
9. **Cleanup**: Clean up temporary files

#### Complete Cart Clinic Workflow
1. **Device Connection**: Connect to Chromatic device
2. **Cartridge Detection**: Insert and detect cartridge
3. **Cartridge Analysis**: Analyze cartridge properties
4. **ROM Reading**: Read ROM data from cartridge
5. **Data Validation**: Validate ROM data integrity
6. **File Operations**: Save ROM to file
7. **Optional Writing**: Write ROM to cartridge (if supported)
8. **Verification**: Verify write operation (if applicable)

## Running Hardware Tests

### Automated Test Suite

#### Full Test Suite
```bash
# Run complete hardware validation
./tests/run_hardware_tests.sh --full
```

#### Individual Test Categories
```bash
# Device tests only
./tests/run_hardware_tests.sh --device

# Firmware tests only
./tests/run_hardware_tests.sh --firmware latest

# Cartridge tests only
./tests/run_hardware_tests.sh --cartridge
```

#### Interactive Test Selection
```bash
# Interactive mode with menu selection
./tests/run_hardware_tests.sh --interactive
```

### Manual Testing Procedures

#### Pre-Test Setup
1. **Hardware Setup**
   - Connect Chromatic device via USB
   - Ensure device is powered and responsive
   - Insert test cartridge (if testing cartridge operations)
   - Verify USB cable is data-capable

2. **Software Setup**
   - Activate Python virtual environment
   - Install all dependencies
   - Verify MRUpdater can be imported
   - Check network connectivity

3. **Environment Verification**
   - Run system diagnostic: `python tests/hardware_validation.py --check-system`
   - Verify USB permissions
   - Check available disk space
   - Confirm network access to firmware servers

#### Test Execution

1. **Start Test Suite**
   ```bash
   cd MRUpdater_Source
   ./tests/run_hardware_tests.sh --interactive
   ```

2. **Monitor Test Progress**
   - Watch console output for progress
   - Check for any error messages
   - Monitor system resources during tests

3. **Review Results**
   - Check test summary output
   - Review detailed JSON results
   - Examine log files for issues

#### Post-Test Analysis

1. **Result Validation**
   - Verify all critical tests passed
   - Investigate any failures or errors
   - Check performance metrics

2. **Log Analysis**
   - Review test logs for warnings
   - Check timing information
   - Look for resource usage patterns

3. **Report Generation**
   - Generate test report
   - Document any issues found
   - Create recommendations for fixes

## Test Result Interpretation

### Success Criteria

**Device Tests:**
- All devices detected successfully
- Communication latency < 100ms
- No connection drops during testing
- Device recovery works correctly

**Firmware Tests:**
- Firmware download completes successfully
- Package validation passes
- Compatibility checks pass
- No network or validation errors

**Cartridge Tests:**
- Cartridge detection works reliably
- ROM reading completes without errors
- Data integrity verified
- Write operations successful (if applicable)

### Failure Analysis

#### Common Failure Patterns

**Device Detection Failures:**
- USB permission issues
- Driver problems
- Hardware connection issues
- Device firmware problems

**Communication Failures:**
- USB cable quality issues
- Power supply problems
- Interference or noise
- Timing/synchronization issues

**Firmware Test Failures:**
- Network connectivity problems
- Server availability issues
- Package corruption
- Compatibility problems

**Cartridge Test Failures:**
- Cartridge connection issues
- Dirty or damaged contacts
- Unsupported cartridge types
- Hardware timing issues

#### Debugging Steps

1. **Check System Logs**
   ```bash
   # Check system console for errors
   log show --predicate 'process == "MRUpdater"' --last 1h
   
   # Check USB system logs
   log show --predicate 'subsystem == "com.apple.iokit.usb"' --last 1h
   ```

2. **Verify Hardware**
   ```bash
   # List USB devices
   system_profiler SPUSBDataType | grep -A 10 -B 5 "Chromatic"
   
   # Check USB permissions
   ls -la /dev/cu.usbmodem*
   ```

3. **Test Network Connectivity**
   ```bash
   # Test firmware server connectivity
   curl -I https://firmware.modretro.com/manifest.json
   
   # Test DNS resolution
   nslookup modretro.com
   ```

4. **Analyze Test Logs**
   - Look for error patterns
   - Check timing information
   - Identify resource constraints

## Performance Benchmarks

### Expected Performance Metrics

**Device Communication:**
- Detection time: < 5 seconds
- Connection establishment: < 2 seconds
- Command response time: < 100ms
- Data transfer rate: > 100 KB/s

**Firmware Operations:**
- Manifest download: < 5 seconds
- Firmware download: < 60 seconds (typical package)
- Package validation: < 10 seconds
- Flash preparation: < 5 seconds

**Cartridge Operations:**
- Cartridge detection: < 2 seconds
- ROM reading (32KB): < 10 seconds
- ROM reading (1MB): < 60 seconds
- ROM writing (32KB): < 30 seconds
- Data verification: < 5 seconds

### Performance Optimization

**Memory Usage:**
- Base application: < 100MB RAM
- During ROM operations: < 200MB RAM
- Peak usage (large ROM): < 500MB RAM

**CPU Usage:**
- Idle: < 5% CPU
- During operations: < 50% CPU
- Peak usage: < 80% CPU

**Disk Usage:**
- Application size: < 200MB
- Temporary files: < 100MB
- Log files: < 50MB

## Continuous Testing

### Automated Testing Setup

1. **CI/CD Integration**
   - Set up automated testing pipeline
   - Run tests on code changes
   - Generate test reports automatically

2. **Scheduled Testing**
   - Daily hardware validation tests
   - Weekly comprehensive test suite
   - Monthly performance benchmarking

3. **Test Environment Management**
   - Maintain dedicated test hardware
   - Keep test cartridges available
   - Monitor test environment health

### Test Data Management

1. **Test Results Storage**
   - Archive test results regularly
   - Maintain historical performance data
   - Track test trends over time

2. **Test Asset Management**
   - Maintain test ROM collection
   - Keep test cartridges organized
   - Document test hardware configurations

## Troubleshooting Test Issues

### Common Test Problems

#### Test Environment Issues
- Python environment problems
- Missing dependencies
- Permission issues
- Network connectivity problems

#### Hardware Issues
- Device connection problems
- USB cable issues
- Power supply problems
- Cartridge contact issues

#### Software Issues
- Application crashes during tests
- Memory leaks or resource issues
- Timing or synchronization problems
- Data corruption issues

### Resolution Strategies

1. **Environment Reset**
   ```bash
   # Clean Python environment
   rm -rf venv
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Hardware Reset**
   - Power cycle all devices
   - Try different USB ports/cables
   - Clean cartridge contacts
   - Check for physical damage

3. **Software Reset**
   ```bash
   # Clear application data
   rm -rf ~/Library/Application\ Support/MRUpdater
   rm -rf ~/Library/Caches/com.modretro.mrupdater
   ```

4. **System Reset**
   - Restart macOS
   - Reset USB system
   - Clear system caches
   - Update system software

## Test Reporting

### Test Report Contents

1. **Executive Summary**
   - Overall test results
   - Success/failure rates
   - Critical issues found
   - Recommendations

2. **Detailed Results**
   - Individual test case results
   - Performance metrics
   - Error analysis
   - Timing information

3. **Hardware Configuration**
   - Test hardware details
   - Software versions
   - Environment configuration
   - Test parameters

4. **Recommendations**
   - Issues to address
   - Performance improvements
   - Test procedure updates
   - Hardware recommendations

### Report Generation

```bash
# Generate comprehensive test report
./tests/run_hardware_tests.sh --full --report
```

The test report includes:
- HTML summary report
- JSON detailed results
- Log files
- Performance charts
- Issue tracking

---

For additional testing support, please refer to the [Troubleshooting Guide](TROUBLESHOOTING.md) or contact the development team.
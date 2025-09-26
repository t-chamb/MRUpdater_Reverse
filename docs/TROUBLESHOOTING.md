# MRUpdater Troubleshooting Guide

This comprehensive guide helps you diagnose and resolve common issues with MRUpdater on macOS.

## Quick Diagnostic Checklist

Before diving into specific issues, run through this quick checklist:

- [ ] **System Requirements**: macOS 10.15+ with 4GB+ RAM
- [ ] **USB Connection**: Chromatic device connected with good cable
- [ ] **Permissions**: USB and network permissions granted
- [ ] **Updates**: Latest version of MRUpdater installed
- [ ] **Logs**: Check recent log entries for errors

## Device Connection Issues

### Chromatic Device Not Detected

**Symptoms:**
- "No device detected" message
- Device list shows empty
- Connection status shows "Disconnected"

**Diagnosis Steps:**

1. **Check Physical Connection**
   ```bash
   # List USB devices to see if Chromatic is recognized
   system_profiler SPUSBDataType | grep -A 10 -B 5 "Chromatic\|0x374E"
   ```

2. **Verify Device Mode**
   - Ensure Chromatic is powered on
   - Check if device is in correct mode (not in sleep/standby)
   - Try power cycling the device

3. **Test USB Port and Cable**
   - Try different USB ports (avoid hubs)
   - Test with a known-good USB cable
   - Try connecting to another computer to verify device works

**Solutions:**

1. **Reset USB Permissions**
   ```bash
   # Remove and re-grant USB permissions
   sudo tccutil reset SystemPolicyAllFiles com.modretro.mrupdater
   ```

2. **Restart USB System**
   ```bash
   # Reset USB system (requires restart)
   sudo kextunload -b com.apple.driver.usb.IOUSBHostFamily
   sudo kextload -b com.apple.driver.usb.IOUSBHostFamily
   ```

3. **Check for Driver Issues**
   ```bash
   # Check for conflicting drivers
   kextstat | grep -i usb
   ```

### Intermittent Connection Drops

**Symptoms:**
- Device connects then disconnects repeatedly
- Operations fail mid-process
- "Device communication error" messages

**Solutions:**

1. **Power Management Settings**
   ```bash
   # Disable USB power management
   sudo pmset -a usbpoweroff 0
   ```

2. **USB Hub Issues**
   - Connect directly to Mac, not through hub
   - If hub required, use powered USB hub

3. **Cable Quality**
   - Use high-quality, short USB cables
   - Avoid cables longer than 3 feet
   - Test with multiple cables

## Firmware Flashing Issues

### Firmware Download Failures

**Symptoms:**
- "Failed to download firmware" error
- Network timeout messages
- Partial downloads that fail

**Diagnosis:**

1. **Check Network Connectivity**
   ```bash
   # Test connectivity to firmware servers
   ping -c 4 modretro.com
   curl -I https://firmware.modretro.com/manifest.json
   ```

2. **DNS Resolution**
   ```bash
   # Test DNS resolution
   nslookup modretro.com
   dig modretro.com
   ```

**Solutions:**

1. **Network Configuration**
   ```bash
   # Flush DNS cache
   sudo dscacheutil -flushcache
   sudo killall -HUP mDNSResponder
   ```

2. **Firewall Settings**
   - Add MRUpdater to firewall exceptions
   - Temporarily disable firewall for testing
   - Check corporate firewall/proxy settings

3. **Alternative DNS**
   ```bash
   # Use Google DNS temporarily
   sudo networksetup -setdnsservers Wi-Fi 8.8.8.8 8.8.4.4
   ```

### FPGA Flashing Failures

**Symptoms:**
- "FPGA flash failed" error
- Device becomes unresponsive during flash
- Verification failures after flash

**Solutions:**

1. **Check openFPGALoader**
   ```bash
   # Verify openFPGALoader is available
   /Applications/MRUpdater.app/Contents/Resources/tools/macos/openFPGALoader --help
   ```

2. **Device Reset**
   - Power cycle Chromatic device
   - Hold reset button for 10 seconds
   - Try flashing in recovery mode

3. **USB Power Issues**
   - Use USB port with sufficient power (avoid low-power ports)
   - Try different USB ports
   - Use powered USB hub if necessary

### MCU Flashing Failures

**Symptoms:**
- "MCU flash failed" error
- ESP32 not responding
- Boot loop after flash attempt

**Solutions:**

1. **Check esptool**
   ```bash
   # Verify esptool is working
   /Applications/MRUpdater.app/Contents/Resources/tools/macos/esptool.py --help
   ```

2. **Boot Mode Issues**
   - Ensure device is in correct boot mode
   - Try manual boot mode entry
   - Check for hardware issues

3. **Serial Communication**
   ```bash
   # Check serial port permissions
   ls -la /dev/cu.usbmodem*
   ```

## Cart Clinic Issues

### Cartridge Not Detected

**Symptoms:**
- "No cartridge inserted" message
- Cartridge info shows as unknown
- Read operations fail immediately

**Solutions:**

1. **Cartridge Connection**
   - Clean cartridge contacts with isopropyl alcohol
   - Ensure cartridge is fully inserted
   - Try different cartridges to isolate issue

2. **Contact Cleaning**
   ```bash
   # Check for oxidation or dirt on contacts
   # Use cotton swab with 99% isopropyl alcohol
   # Allow to dry completely before testing
   ```

3. **Cartridge Compatibility**
   - Verify cartridge type is supported
   - Check for unusual mapper types
   - Test with known-good cartridges

### ROM Reading Failures

**Symptoms:**
- Read operation starts but fails partway through
- Corrupted ROM data
- Checksum verification failures

**Solutions:**

1. **Memory Management**
   ```bash
   # Check available memory
   vm_stat
   # Close other applications to free memory
   ```

2. **Read Speed Issues**
   - Reduce read speed in settings
   - Enable error correction
   - Use multiple read attempts

3. **Data Integrity**
   - Compare multiple reads of same ROM
   - Verify checksums against known good dumps
   - Check for intermittent connection issues

### ROM Writing Failures

**Symptoms:**
- Write operation fails
- Verification errors after write
- Cartridge becomes unreadable

**Solutions:**

1. **Write Protection**
   - Check if cartridge has write protection
   - Verify cartridge supports writing
   - Check for hardware write protection

2. **Power Issues**
   - Ensure stable power during write
   - Use high-quality USB cable
   - Avoid USB hubs during write operations

3. **Timing Issues**
   - Adjust write timing in advanced settings
   - Try slower write speeds
   - Enable write verification

## Performance Issues

### Slow Application Startup

**Symptoms:**
- Application takes long time to launch
- Splash screen shows for extended period
- UI becomes unresponsive during startup

**Diagnosis:**

1. **System Resources**
   ```bash
   # Check system load
   top -l 1 | head -20
   
   # Check memory usage
   vm_stat
   
   # Check disk space
   df -h
   ```

2. **Application Logs**
   ```bash
   # Check startup logs
   tail -f ~/Library/Logs/MRUpdater/mrupdater.log
   ```

**Solutions:**

1. **Free System Resources**
   - Close unnecessary applications
   - Restart Mac to clear memory
   - Free up disk space (need 1GB+ free)

2. **Reset Application Data**
   ```bash
   # Clear application cache
   rm -rf ~/Library/Caches/com.modretro.mrupdater
   
   # Reset preferences (will lose settings)
   rm ~/Library/Preferences/com.modretro.mrupdater.plist
   ```

3. **Disable Startup Items**
   - Check System Preferences > Users & Groups > Login Items
   - Disable unnecessary startup applications

### Memory Issues with Large ROMs

**Symptoms:**
- Application crashes when handling large ROMs (>32MB)
- "Out of memory" errors
- System becomes unresponsive

**Solutions:**

1. **Increase Available Memory**
   ```bash
   # Check memory pressure
   memory_pressure
   
   # Force garbage collection
   sudo purge
   ```

2. **Optimize ROM Handling**
   - Process ROMs in smaller chunks
   - Enable memory-efficient mode in settings
   - Close other applications during ROM operations

3. **System Upgrade**
   - Consider upgrading RAM if consistently running low
   - Use external storage for temporary files

## Application Crashes

### Startup Crashes

**Symptoms:**
- Application quits immediately after launch
- "MRUpdater quit unexpectedly" dialog
- No UI appears

**Diagnosis:**

1. **Crash Reports**
   ```bash
   # Find crash reports
   ls -la ~/Library/Logs/DiagnosticReports/MRUpdater*
   
   # View most recent crash
   cat ~/Library/Logs/DiagnosticReports/MRUpdater_*.crash
   ```

2. **Console Logs**
   ```bash
   # Check system console for errors
   log show --predicate 'process == "MRUpdater"' --last 1h
   ```

**Solutions:**

1. **Clean Installation**
   ```bash
   # Remove application completely
   rm -rf /Applications/MRUpdater.app
   rm -rf ~/Library/Preferences/com.modretro.mrupdater.plist
   rm -rf ~/Library/Application\ Support/MRUpdater
   
   # Reinstall from fresh download
   ```

2. **System Compatibility**
   - Verify macOS version compatibility
   - Check for system updates
   - Verify hardware compatibility (Intel vs Apple Silicon)

3. **Permission Issues**
   ```bash
   # Reset all permissions
   sudo tccutil reset All com.modretro.mrupdater
   ```

### Operation Crashes

**Symptoms:**
- Application crashes during specific operations
- Crashes when connecting device
- Crashes during firmware flash or ROM operations

**Solutions:**

1. **Identify Crash Pattern**
   - Note exactly when crashes occur
   - Try to reproduce with minimal steps
   - Check if specific devices/ROMs cause crashes

2. **Safe Mode Operation**
   - Launch with minimal features enabled
   - Disable advanced features temporarily
   - Use basic operations only

3. **Hardware Issues**
   - Test with different devices
   - Try different USB ports/cables
   - Check for hardware conflicts

## Network and Security Issues

### Firewall Blocking

**Symptoms:**
- Cannot download firmware updates
- Network operations timeout
- "Connection refused" errors

**Solutions:**

1. **Firewall Configuration**
   ```bash
   # Check firewall status
   sudo /usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate
   
   # Add MRUpdater to firewall exceptions
   sudo /usr/libexec/ApplicationFirewall/socketfilterfw --add /Applications/MRUpdater.app/Contents/MacOS/MRUpdater
   ```

2. **Network Diagnostics**
   ```bash
   # Test specific endpoints
   nc -zv firmware.modretro.com 443
   curl -v https://api.modretro.com/health
   ```

### Certificate Issues

**Symptoms:**
- SSL/TLS certificate errors
- "Untrusted server" warnings
- HTTPS connection failures

**Solutions:**

1. **Update Certificates**
   ```bash
   # Update system certificates
   sudo /usr/sbin/update_dyld_shared_cache
   
   # Check certificate validity
   openssl s_client -connect modretro.com:443 -servername modretro.com
   ```

2. **Time Synchronization**
   ```bash
   # Check system time
   date
   
   # Sync time if needed
   sudo sntp -sS time.apple.com
   ```

## Advanced Diagnostics

### Comprehensive System Check

Run this comprehensive diagnostic script:

```bash
#!/bin/bash
# MRUpdater System Diagnostic Script

echo "=== MRUpdater System Diagnostic ==="
echo "Date: $(date)"
echo "User: $(whoami)"
echo ""

echo "=== System Information ==="
sw_vers
echo "Hardware: $(system_profiler SPHardwareDataType | grep 'Model Name\|Chip\|Memory')"
echo ""

echo "=== USB Devices ==="
system_profiler SPUSBDataType | grep -A 5 -B 5 "Chromatic\|0x374E" || echo "No Chromatic device found"
echo ""

echo "=== Network Connectivity ==="
ping -c 3 modretro.com || echo "Cannot reach modretro.com"
curl -I https://firmware.modretro.com/manifest.json || echo "Cannot reach firmware server"
echo ""

echo "=== Application Status ==="
ls -la /Applications/MRUpdater.app || echo "MRUpdater not installed"
ps aux | grep MRUpdater | grep -v grep || echo "MRUpdater not running"
echo ""

echo "=== Permissions ==="
ls -la ~/Library/Preferences/com.modretro.mrupdater.plist || echo "No preferences file"
ls -la ~/Library/Application\ Support/MRUpdater || echo "No application support directory"
echo ""

echo "=== Recent Logs ==="
if [ -f ~/Library/Logs/MRUpdater/mrupdater.log ]; then
    echo "Last 10 log entries:"
    tail -10 ~/Library/Logs/MRUpdater/mrupdater.log
else
    echo "No log file found"
fi
echo ""

echo "=== Crash Reports ==="
ls -la ~/Library/Logs/DiagnosticReports/MRUpdater* 2>/dev/null || echo "No crash reports found"
echo ""

echo "=== System Resources ==="
echo "Memory:"
vm_stat | head -5
echo "Disk Space:"
df -h / | tail -1
echo "Load Average:"
uptime
echo ""

echo "=== Diagnostic Complete ==="
```

### Log Analysis

Key log patterns to look for:

1. **Connection Issues**
   ```
   ERROR: Device not found
   WARNING: USB communication timeout
   ERROR: Failed to establish session
   ```

2. **Memory Issues**
   ```
   ERROR: Out of memory
   WARNING: Memory pressure detected
   ERROR: Failed to allocate buffer
   ```

3. **Network Issues**
   ```
   ERROR: Download failed
   WARNING: Network timeout
   ERROR: SSL certificate error
   ```

## Getting Additional Help

### Information to Collect

When seeking help, gather this information:

1. **System Information**
   ```bash
   sw_vers > system_info.txt
   system_profiler SPHardwareDataType >> system_info.txt
   ```

2. **Application Logs**
   ```bash
   cp ~/Library/Logs/MRUpdater/mrupdater.log ./
   ```

3. **Crash Reports**
   ```bash
   cp ~/Library/Logs/DiagnosticReports/MRUpdater_*.crash ./
   ```

4. **Network Diagnostics**
   ```bash
   ping -c 5 modretro.com > network_test.txt
   traceroute modretro.com >> network_test.txt
   ```

### Support Channels

1. **GitHub Issues**: For bugs and feature requests
2. **Community Forums**: For general help and discussion
3. **Email Support**: For critical issues requiring immediate attention
4. **Documentation**: Check official docs for updates

### Emergency Recovery

If MRUpdater becomes completely unusable:

1. **Safe Mode Boot**
   - Boot Mac in Safe Mode
   - Try launching MRUpdater with minimal system load

2. **Clean Reinstall**
   ```bash
   # Complete removal and reinstall
   rm -rf /Applications/MRUpdater.app
   rm -rf ~/Library/Preferences/com.modretro.mrupdater*
   rm -rf ~/Library/Application\ Support/MRUpdater
   rm -rf ~/Library/Caches/com.modretro.mrupdater
   # Download and reinstall fresh copy
   ```

3. **System Recovery**
   - If system becomes unstable, restart in Recovery Mode
   - Run Disk Utility to check for disk errors
   - Reset NVRAM/PRAM if necessary

---

For additional support, please visit the [MRUpdater GitHub repository](https://github.com/modretro/mrupdater) or contact our support team with the diagnostic information collected above.
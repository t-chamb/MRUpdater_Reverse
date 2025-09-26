# MRUpdater Installation Guide

This guide provides detailed instructions for installing and running MRUpdater on macOS.

## System Requirements

### Minimum Requirements
- **macOS**: 10.15 (Catalina) or later
- **RAM**: 4 GB minimum, 8 GB recommended
- **Storage**: 500 MB free space
- **USB**: USB 2.0 or higher port for device connection

### Recommended Requirements
- **macOS**: 12.0 (Monterey) or later
- **RAM**: 8 GB or more
- **Storage**: 1 GB free space
- **USB**: USB 3.0 port for faster data transfer

### Hardware Compatibility
- **Intel Macs**: All Intel-based Macs from 2015 onwards
- **Apple Silicon**: M1, M1 Pro, M1 Max, M2, and newer chips
- **USB-C**: USB-C to USB-A adapter may be required for newer Macs

## Installation Methods

### Method 1: DMG Installer (Recommended)

1. **Download the DMG**
   - Download `MRUpdater.dmg` from the official release page
   - Verify the download is complete (file size should match the published size)

2. **Open the DMG**
   - Double-click the downloaded DMG file
   - If you see a security warning, click "Open" to proceed
   - The DMG will mount and show the installer window

3. **Install the Application**
   - Drag the `MRUpdater.app` icon to the `Applications` folder
   - Wait for the copy operation to complete
   - Eject the DMG by clicking the eject button or dragging it to Trash

4. **First Launch**
   - Open `Applications` folder in Finder
   - Double-click `MRUpdater.app` to launch
   - If you see a security dialog, follow the steps in the "Security" section below

### Method 2: Direct App Bundle

1. **Download the App**
   - Download `MRUpdater.app.zip` from the release page
   - Extract the ZIP file by double-clicking it

2. **Move to Applications**
   - Drag the extracted `MRUpdater.app` to your `Applications` folder
   - Alternatively, you can run it from any location

3. **Launch the Application**
   - Double-click `MRUpdater.app` to launch
   - Follow security steps if prompted

## Security and Permissions

### Gatekeeper and Code Signing

MRUpdater is signed with a valid Developer ID certificate. However, you may still encounter security warnings on first launch.

**If you see "MRUpdater cannot be opened because it is from an unidentified developer":**

1. **Method 1: System Preferences**
   - Go to `System Preferences` > `Security & Privacy`
   - Click the `General` tab
   - You should see a message about MRUpdater being blocked
   - Click `Open Anyway`
   - Confirm by clicking `Open` in the dialog

2. **Method 2: Right-click Override**
   - Right-click on `MRUpdater.app` in Applications
   - Select `Open` from the context menu
   - Click `Open` in the security dialog

3. **Method 3: Terminal Command**
   ```bash
   sudo spctl --master-disable
   # Launch MRUpdater, then re-enable Gatekeeper:
   sudo spctl --master-enable
   ```

### USB Device Permissions

MRUpdater needs permission to access USB devices to communicate with Chromatic hardware.

**Granting USB Permissions:**

1. **System Preferences Method**
   - Go to `System Preferences` > `Security & Privacy`
   - Click the `Privacy` tab
   - Select `USB` from the left sidebar
   - Check the box next to `MRUpdater`

2. **Automatic Prompt**
   - When you first connect a Chromatic device, macOS may prompt for permission
   - Click `Allow` to grant USB access

### Network Permissions

MRUpdater requires network access to download firmware updates.

**If network access is blocked:**
- Go to `System Preferences` > `Security & Privacy` > `Privacy` > `Network`
- Ensure `MRUpdater` is checked in the list

## Troubleshooting

### Common Installation Issues

#### "App is damaged and can't be opened"

This usually indicates a corrupted download or quarantine issue.

**Solutions:**
1. **Re-download the application**
   - Delete the current download
   - Clear browser cache
   - Download again from the official source

2. **Remove quarantine attribute**
   ```bash
   sudo xattr -rd com.apple.quarantine /Applications/MRUpdater.app
   ```

3. **Verify download integrity**
   - Check the file size matches the published size
   - Verify SHA256 checksum if provided

#### "MRUpdater quit unexpectedly"

This indicates a crash during startup.

**Solutions:**
1. **Check system requirements**
   - Ensure your macOS version is supported
   - Verify sufficient RAM and storage

2. **Reset application preferences**
   ```bash
   rm -rf ~/Library/Preferences/com.modretro.mrupdater.plist
   rm -rf ~/Library/Application\ Support/MRUpdater
   ```

3. **Check Console logs**
   - Open `Console.app`
   - Look for MRUpdater crash reports
   - Check for specific error messages

#### "No Chromatic device detected"

The application can't find connected Chromatic hardware.

**Solutions:**
1. **Check USB connection**
   - Try a different USB cable
   - Use a different USB port
   - Avoid USB hubs if possible

2. **Verify device mode**
   - Ensure Chromatic is in the correct mode
   - Try restarting the device
   - Check device firmware version

3. **Reset USB permissions**
   - Go to `System Preferences` > `Security & Privacy` > `Privacy` > `USB`
   - Remove MRUpdater from the list
   - Restart MRUpdater to re-request permissions

### Performance Issues

#### Slow startup or operation

**Solutions:**
1. **Free up system resources**
   - Close unnecessary applications
   - Ensure sufficient free RAM (4GB+)
   - Check available storage space

2. **Reset application data**
   ```bash
   rm -rf ~/Library/Caches/com.modretro.mrupdater
   rm -rf ~/Library/Application\ Support/MRUpdater/logs
   ```

3. **Check for background processes**
   - Open `Activity Monitor`
   - Look for high CPU usage processes
   - Quit unnecessary applications

#### Large ROM file handling

For ROMs larger than 32MB:

1. **Increase available RAM**
   - Close other applications
   - Restart your Mac if necessary

2. **Use external storage**
   - Save ROM files to external drive with fast connection
   - Avoid network drives for large files

3. **Monitor memory usage**
   - Use Activity Monitor to watch memory usage
   - Consider upgrading RAM if consistently running low

### Network Issues

#### Firmware download failures

**Solutions:**
1. **Check internet connection**
   - Verify internet connectivity
   - Try accessing other websites

2. **Firewall and security software**
   - Temporarily disable firewall
   - Check antivirus software settings
   - Add MRUpdater to security software whitelist

3. **DNS issues**
   - Try using different DNS servers (8.8.8.8, 1.1.1.1)
   - Flush DNS cache: `sudo dscacheutil -flushcache`

4. **Proxy settings**
   - Check system proxy settings
   - Configure proxy in MRUpdater if needed

## Advanced Configuration

### Command Line Options

MRUpdater supports several command line options for advanced users:

```bash
# Launch with debug logging
/Applications/MRUpdater.app/Contents/MacOS/MRUpdater --debug

# Skip splash screen
/Applications/MRUpdater.app/Contents/MacOS/MRUpdater --no-splash

# Show version information
/Applications/MRUpdater.app/Contents/MacOS/MRUpdater --version
```

### Configuration Files

MRUpdater stores configuration in:
- **Preferences**: `~/Library/Preferences/com.modretro.mrupdater.plist`
- **Application Support**: `~/Library/Application Support/MRUpdater/`
- **Logs**: `~/Library/Logs/MRUpdater/`
- **Cache**: `~/Library/Caches/com.modretro.mrupdater/`

### Environment Variables

Advanced users can set environment variables to modify behavior:

```bash
# Enable debug mode
export MRUPDATER_DEBUG=1

# Set custom log level
export MRUPDATER_LOG_LEVEL=DEBUG

# Use custom firmware server
export MRUPDATER_FIRMWARE_URL=https://custom.server.com
```

## Uninstallation

### Complete Removal

To completely remove MRUpdater from your system:

1. **Delete the application**
   ```bash
   rm -rf /Applications/MRUpdater.app
   ```

2. **Remove user data**
   ```bash
   rm -rf ~/Library/Preferences/com.modretro.mrupdater.plist
   rm -rf ~/Library/Application\ Support/MRUpdater
   rm -rf ~/Library/Caches/com.modretro.mrupdater
   rm -rf ~/Library/Logs/MRUpdater
   ```

3. **Remove system-wide data** (if any)
   ```bash
   sudo rm -rf /Library/Application\ Support/MRUpdater
   sudo rm -rf /Library/Preferences/com.modretro.mrupdater.plist
   ```

### Partial Removal (Keep Settings)

To remove the application but keep settings and logs:

```bash
rm -rf /Applications/MRUpdater.app
```

Settings and logs will be preserved for future installations.

## Getting Help

### Log Files

When reporting issues, include relevant log files:

- **Application logs**: `~/Library/Logs/MRUpdater/mrupdater.log`
- **System logs**: Use Console.app to find MRUpdater entries
- **Crash reports**: `~/Library/Logs/DiagnosticReports/MRUpdater*`

### Support Channels

1. **GitHub Issues**: Report bugs and feature requests
2. **Community Forums**: Get help from other users
3. **Documentation**: Check the official documentation
4. **Email Support**: Contact support for critical issues

### Information to Include

When seeking help, please provide:

- **macOS version**: `sw_vers`
- **MRUpdater version**: Check About dialog
- **Hardware details**: Mac model, year, chip type
- **Error messages**: Exact text of any error messages
- **Steps to reproduce**: Detailed steps that cause the issue
- **Log files**: Relevant portions of log files

## Updates

### Automatic Updates

MRUpdater can check for updates automatically:

1. **Enable auto-update checking**
   - Go to Preferences > Updates
   - Check "Check for updates automatically"

2. **Manual update check**
   - Go to Help > Check for Updates
   - Follow prompts to download and install

### Manual Updates

1. **Download new version**
   - Download the latest DMG from the release page
   - Follow installation steps above

2. **Replace existing installation**
   - The new version will replace the old one
   - Settings and data are preserved

## Security Best Practices

### Download Verification

Always download MRUpdater from official sources:

- **Official GitHub releases**
- **ModRetro website**
- **Verified distribution partners**

### Checksum Verification

Verify download integrity using SHA256:

```bash
shasum -a 256 MRUpdater.dmg
# Compare with published checksum
```

### Keep Updated

- Enable automatic update checking
- Install security updates promptly
- Monitor release notes for security fixes

---

For additional help, please visit the [MRUpdater GitHub repository](https://github.com/modretro/mrupdater) or contact support.
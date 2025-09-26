# MCU flashing workflow for Chromatic devices
# Implements esptool integration with reset management and verification

import os
import subprocess
import logging
import time
import re
import json
from dataclasses import dataclass
from typing import Optional, Callable, Dict, Any, List
from pathlib import Path

from .util import get_esptool_bin_path
from .constants import CHROMATIC_VID, CHROMATIC_PID
from .device_communication import DeviceCommunicationManager
from .version_detector import FirmwareVersion

logger = logging.getLogger('mrupdater.mcu_flasher')

@dataclass
class MCUFlashProgress:
    """MCU flashing progress information"""
    stage: str
    progress_percent: float
    current_operation: str
    bytes_written: int = 0
    total_bytes: int = 0
    elapsed_time: float = 0.0
    estimated_remaining: Optional[float] = None

class MCUFlashError(Exception):
    """Raised when MCU flashing fails"""
    pass

class MCUDetectionError(Exception):
    """Raised when MCU detection fails"""
    pass

class MCUFlasher:
    """
    Handles MCU firmware flashing for Chromatic devices.
    
    Integrates with esptool for ESP32 operations, provides progress monitoring,
    reset and boot mode management, and verification capabilities.
    """
    
    def __init__(self, device_communicator: Optional[DeviceCommunicationManager] = None):
        self.device_communicator = device_communicator
        self.logger = logging.getLogger('mrupdater.mcu_flasher')
        
        # Get esptool binary path
        self.esptool_path = get_esptool_bin_path()
        if not self.esptool_path:
            raise MCUFlashError("esptool not found")
        
        self.logger.info(f"Using esptool at: {self.esptool_path}")
        
        # ESP32 flash configuration
        self.flash_config = {
            'baud_rate': 921600,
            'flash_size': '4MB',
            'flash_mode': 'dio',
            'flash_freq': '40m',
            'bootloader_offset': '0x1000',
            'partition_table_offset': '0x8000',
            'app_offset': '0x10000'
        }
    
    def detect_mcu_devices(self) -> List[Dict[str, Any]]:
        """
        Detect connected ESP32 devices.
        
        Returns:
            List[Dict[str, Any]]: List of detected ESP32 devices
        """
        try:
            self.logger.info("Detecting ESP32 devices...")
            
            # Use esptool to detect connected devices
            cmd = self._build_esptool_cmd(['--port', 'auto', 'chip_id'])
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                self.logger.error(f"ESP32 detection failed: {result.stderr}")
                raise MCUDetectionError(f"Detection failed: {result.stderr}")
            
            # Parse detection output
            devices = self._parse_detection_output(result.stdout)
            
            self.logger.info(f"Detected {len(devices)} ESP32 device(s)")
            for device in devices:
                self.logger.info(f"  - {device['chip_type']} on {device['port']}")
            
            return devices
            
        except subprocess.TimeoutExpired:
            self.logger.error("ESP32 detection timed out")
            raise MCUDetectionError("Detection timed out")
        except Exception as e:
            self.logger.error(f"Error detecting ESP32 devices: {e}")
            raise MCUDetectionError(f"Detection error: {e}")
    
    def _parse_detection_output(self, output: str) -> List[Dict[str, Any]]:
        """
        Parse esptool detection output.
        
        Args:
            output: Raw detection output
            
        Returns:
            List[Dict[str, Any]]: Parsed device information
        """
        devices = []
        
        try:
            lines = output.strip().split('\n')
            current_device = {}
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Look for chip type
                chip_match = re.search(r'Chip is (ESP32[^,\s]*)', line)
                if chip_match:
                    current_device['chip_type'] = chip_match.group(1)
                
                # Look for MAC address
                mac_match = re.search(r'MAC: ([0-9a-fA-F:]{17})', line)
                if mac_match:
                    current_device['mac_address'] = mac_match.group(1)
                
                # Look for flash size
                flash_match = re.search(r'Flash size: (\d+MB)', line)
                if flash_match:
                    current_device['flash_size'] = flash_match.group(1)
                
                # Look for port information (from command line)
                port_match = re.search(r'Serial port (.+)', line)
                if port_match:
                    current_device['port'] = port_match.group(1)
                
                # If we have basic info, add device
                if 'chip_type' in current_device and current_device not in devices:
                    # Set default port if not found
                    if 'port' not in current_device:
                        current_device['port'] = 'auto'
                    
                    devices.append(current_device.copy())
        
        except Exception as e:
            self.logger.warning(f"Error parsing detection output: {e}")
        
        return devices
    
    def flash_mcu_firmware(self, firmware_path: str, 
                          port: Optional[str] = None,
                          progress_callback: Optional[Callable[[MCUFlashProgress], None]] = None) -> bool:
        """
        Flash MCU firmware to ESP32 device.
        
        Args:
            firmware_path: Path to firmware binary file
            port: Serial port to use (auto-detected if None)
            progress_callback: Optional callback for progress updates
            
        Returns:
            bool: True if flashing succeeded
        """
        try:
            self.logger.info(f"Starting MCU firmware flash: {firmware_path}")
            
            # Validate firmware file
            if not os.path.exists(firmware_path):
                raise MCUFlashError(f"Firmware file not found: {firmware_path}")
            
            file_size = os.path.getsize(firmware_path)
            self.logger.info(f"Firmware file size: {file_size} bytes")
            
            # Detect port if not specified
            if not port:
                devices = self.detect_mcu_devices()
                if not devices:
                    raise MCUFlashError("No ESP32 devices detected")
                
                port = devices[0].get('port', 'auto')
                self.logger.info(f"Using auto-detected port: {port}")
            
            # Enter bootloader mode
            if progress_callback:
                progress_callback(MCUFlashProgress(
                    stage="preparing",
                    progress_percent=0.0,
                    current_operation="Entering bootloader mode...",
                    total_bytes=file_size
                ))
            
            if not self._enter_bootloader_mode(port):
                raise MCUFlashError("Failed to enter bootloader mode")
            
            # Flash firmware
            start_time = time.time()
            success = self._flash_firmware_file(firmware_path, port, progress_callback, start_time)
            
            if success:
                elapsed_time = time.time() - start_time
                self.logger.info(f"MCU flashing completed successfully in {elapsed_time:.2f}s")
                
                if progress_callback:
                    progress_callback(MCUFlashProgress(
                        stage="completed",
                        progress_percent=100.0,
                        current_operation="Flash completed successfully",
                        bytes_written=file_size,
                        total_bytes=file_size,
                        elapsed_time=elapsed_time
                    ))
                
                # Reset device and verify
                self._reset_device(port)
                
                if self.device_communicator:
                    self._verify_mcu_flash()
                
                return True
            else:
                raise MCUFlashError("MCU flashing failed")
                
        except Exception as e:
            self.logger.error(f"MCU flashing error: {e}")
            if progress_callback:
                progress_callback(MCUFlashProgress(
                    stage="error",
                    progress_percent=0.0,
                    current_operation=f"Error: {e}"
                ))
            raise MCUFlashError(f"MCU flashing failed: {e}") 
   
    def _enter_bootloader_mode(self, port: str) -> bool:
        """
        Enter ESP32 bootloader mode.
        
        Args:
            port: Serial port
            
        Returns:
            bool: True if bootloader mode entered successfully
        """
        try:
            self.logger.info("Entering ESP32 bootloader mode...")
            
            # Try to connect and enter bootloader mode
            cmd = self._build_esptool_cmd(['--port', port, '--baud', str(self.flash_config['baud_rate']), 'chip_id'])
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                self.logger.info("Successfully entered bootloader mode")
                return True
            else:
                self.logger.error(f"Failed to enter bootloader mode: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error entering bootloader mode: {e}")
            return False
    
    def _flash_firmware_file(self, firmware_path: str, port: str,
                           progress_callback: Optional[Callable[[MCUFlashProgress], None]],
                           start_time: float) -> bool:
        """
        Flash firmware file to ESP32.
        
        Args:
            firmware_path: Path to firmware file
            port: Serial port
            progress_callback: Progress callback function
            start_time: Start time for elapsed calculation
            
        Returns:
            bool: True if flashing succeeded
        """
        try:
            # Build flash command
            cmd = self._build_esptool_cmd([
                '--port', port,
                '--baud', str(self.flash_config['baud_rate']),
                'write_flash',
                '--flash_mode', self.flash_config['flash_mode'],
                '--flash_freq', self.flash_config['flash_freq'],
                '--flash_size', self.flash_config['flash_size'],
                self.flash_config['app_offset'],
                firmware_path
            ])
            
            self.logger.info(f"Flash command: {' '.join(cmd)}")
            
            # Start flashing process
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            file_size = os.path.getsize(firmware_path)
            bytes_written = 0
            current_stage = "flashing"
            
            # Monitor process output
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                
                if output:
                    line = output.strip()
                    self.logger.debug(f"esptool: {line}")
                    
                    # Parse progress information
                    progress_info = self._parse_flash_output(line, file_size)
                    if progress_info:
                        bytes_written = progress_info.get('bytes_written', bytes_written)
                        current_stage = progress_info.get('stage', current_stage)
                        
                        if progress_callback:
                            elapsed_time = time.time() - start_time
                            progress_percent = (bytes_written / file_size * 100) if file_size > 0 else 0
                            
                            # Estimate remaining time
                            estimated_remaining = None
                            if bytes_written > 0 and elapsed_time > 0:
                                bytes_per_second = bytes_written / elapsed_time
                                remaining_bytes = file_size - bytes_written
                                estimated_remaining = remaining_bytes / bytes_per_second
                            
                            progress_callback(MCUFlashProgress(
                                stage=current_stage,
                                progress_percent=progress_percent,
                                current_operation=line,
                                bytes_written=bytes_written,
                                total_bytes=file_size,
                                elapsed_time=elapsed_time,
                                estimated_remaining=estimated_remaining
                            ))
            
            # Wait for process completion
            return_code = process.wait(timeout=300)  # 5 minute timeout
            
            if return_code == 0:
                self.logger.info("esptool completed successfully")
                return True
            else:
                self.logger.error(f"esptool failed with return code {return_code}")
                return False
                
        except subprocess.TimeoutExpired:
            self.logger.error("MCU flashing process timed out")
            process.kill()
            return False
        except Exception as e:
            self.logger.error(f"Error running flash process: {e}")
            return False
    
    def _parse_flash_output(self, line: str, file_size: int) -> Optional[Dict[str, Any]]:
        """
        Parse esptool output for progress information.
        
        Args:
            line: Output line from esptool
            file_size: Total file size for percentage calculation
            
        Returns:
            Dict[str, Any]: Parsed progress information, or None
        """
        progress_info = {}
        
        try:
            # Look for various progress indicators
            
            # Percentage progress: "Writing at 0x00010000... (50 %)"
            percent_match = re.search(r'\((\d+)\s*%\)', line)
            if percent_match:
                percent = int(percent_match.group(1))
                progress_info['bytes_written'] = int(file_size * percent / 100)
                progress_info['stage'] = 'writing'
                return progress_info
            
            # Address progress: "Writing at 0x00012000..."
            addr_match = re.search(r'Writing at 0x([0-9a-fA-F]+)', line)
            if addr_match:
                addr = int(addr_match.group(1), 16)
                app_offset = int(self.flash_config['app_offset'], 16)
                if addr >= app_offset:
                    bytes_written = addr - app_offset
                    progress_info['bytes_written'] = min(bytes_written, file_size)
                    progress_info['stage'] = 'writing'
                    return progress_info
            
            # Stage detection
            if 'erasing' in line.lower():
                progress_info['stage'] = 'erasing'
            elif 'writing' in line.lower():
                progress_info['stage'] = 'writing'
            elif 'verifying' in line.lower():
                progress_info['stage'] = 'verifying'
            elif 'connecting' in line.lower():
                progress_info['stage'] = 'connecting'
            
            if progress_info:
                return progress_info
                
        except Exception as e:
            self.logger.debug(f"Error parsing flash output: {e}")
        
        return None    

    def _reset_device(self, port: str) -> bool:
        """
        Reset ESP32 device after flashing.
        
        Args:
            port: Serial port
            
        Returns:
            bool: True if reset succeeded
        """
        try:
            self.logger.info("Resetting ESP32 device...")
            
            # Use esptool to reset the device
            cmd = self._build_esptool_cmd(['--port', port, 'run'])
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                self.logger.info("ESP32 reset completed successfully")
                time.sleep(2.0)  # Wait for device to boot
                return True
            else:
                self.logger.warning(f"ESP32 reset command failed: {result.stderr}")
                # Reset failure is not critical, device may still boot
                return True
                
        except Exception as e:
            self.logger.warning(f"Error resetting ESP32: {e}")
            return True  # Non-critical failure
    
    def _verify_mcu_flash(self) -> bool:
        """
        Verify MCU flash by checking device communication.
        
        Returns:
            bool: True if verification succeeded
        """
        try:
            self.logger.info("Verifying MCU flash...")
            
            # Wait for device to boot
            time.sleep(3.0)
            
            # Try to establish communication
            if not self.device_communicator.connect():
                self.logger.warning("Could not establish communication after MCU flash")
                return False
            
            # Query device version to verify MCU is responding
            from .version_detector import VersionDetector
            version_detector = VersionDetector(self.device_communicator.transport)
            
            device_version = version_detector.get_device_version(timeout=10.0)
            if device_version:
                self.logger.info(f"MCU flash verification successful - MCU version: {device_version.mcu_version}")
                return True
            else:
                self.logger.warning("Could not query device version after MCU flash")
                return False
                
        except Exception as e:
            self.logger.warning(f"MCU flash verification failed: {e}")
            return False
    
    def _build_esptool_cmd(self, args: List[str]) -> List[str]:
        """
        Build esptool command with proper executable handling.
        
        Args:
            args: Command arguments
            
        Returns:
            List[str]: Complete command
        """
        if self.esptool_path.endswith(' -m esptool'):
            # Python module invocation
            python_exe, module_args = self.esptool_path.split(' -m ')
            return [python_exe, '-m', 'esptool'] + args
        else:
            # Direct executable
            return [self.esptool_path] + args
    
    def get_mcu_info(self, port: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Get MCU device information.
        
        Args:
            port: Serial port (auto-detected if None)
            
        Returns:
            Dict[str, Any]: MCU device information, or None if failed
        """
        try:
            if not port:
                devices = self.detect_mcu_devices()
                if not devices:
                    return None
                port = devices[0].get('port', 'auto')
            
            # Get chip info
            cmd = self._build_esptool_cmd(['--port', port, 'chip_id'])
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                return None
            
            # Parse chip information
            info = self._parse_chip_info(result.stdout)
            info['port'] = port
            
            # Add version info if device communicator is available
            if self.device_communicator and self.device_communicator.is_connected():
                try:
                    from .version_detector import VersionDetector
                    version_detector = VersionDetector(self.device_communicator.transport)
                    
                    device_version = version_detector.get_device_version()
                    if device_version:
                        info['firmware_version'] = device_version.mcu_version
                        info['fpga_version'] = device_version.fpga_version
                        
                except Exception as e:
                    self.logger.debug(f"Could not get device version: {e}")
            
            return info
            
        except Exception as e:
            self.logger.error(f"Error getting MCU info: {e}")
            return None
    
    def _parse_chip_info(self, output: str) -> Dict[str, Any]:
        """
        Parse esptool chip info output.
        
        Args:
            output: Raw chip info output
            
        Returns:
            Dict[str, Any]: Parsed chip information
        """
        info = {}
        
        try:
            lines = output.strip().split('\n')
            
            for line in lines:
                line = line.strip()
                
                # Chip type
                chip_match = re.search(r'Chip is (ESP32[^,\s]*)', line)
                if chip_match:
                    info['chip_type'] = chip_match.group(1)
                
                # Features
                features_match = re.search(r'Features: (.+)', line)
                if features_match:
                    info['features'] = [f.strip() for f in features_match.group(1).split(',')]
                
                # Crystal frequency
                crystal_match = re.search(r'Crystal is (\d+MHz)', line)
                if crystal_match:
                    info['crystal_freq'] = crystal_match.group(1)
                
                # MAC address
                mac_match = re.search(r'MAC: ([0-9a-fA-F:]{17})', line)
                if mac_match:
                    info['mac_address'] = mac_match.group(1)
                
                # Flash size
                flash_match = re.search(r'Flash size: (\d+MB)', line)
                if flash_match:
                    info['flash_size'] = flash_match.group(1)
        
        except Exception as e:
            self.logger.warning(f"Error parsing chip info: {e}")
        
        return info
    
    def check_mcu_compatibility(self, firmware_path: str) -> Dict[str, Any]:
        """
        Check MCU firmware compatibility.
        
        Args:
            firmware_path: Path to firmware file
            
        Returns:
            Dict[str, Any]: Compatibility check results
        """
        compatibility = {
            'compatible': False,
            'file_exists': False,
            'file_size': 0,
            'file_format': 'unknown',
            'warnings': [],
            'errors': []
        }
        
        try:
            # Check file existence
            if not os.path.exists(firmware_path):
                compatibility['errors'].append(f"Firmware file not found: {firmware_path}")
                return compatibility
            
            compatibility['file_exists'] = True
            compatibility['file_size'] = os.path.getsize(firmware_path)
            
            # Check file extension
            file_ext = Path(firmware_path).suffix.lower()
            if file_ext == '.bin':
                compatibility['file_format'] = 'ESP32 binary'
            elif file_ext == '.elf':
                compatibility['file_format'] = 'ELF executable'
                compatibility['warnings'].append("ELF format detected - binary format preferred for flashing")
            else:
                compatibility['warnings'].append(f"Unknown firmware format: {file_ext}")
            
            # Check file size (typical ESP32 firmware is 1-4MB)
            if compatibility['file_size'] < 10000:  # 10KB
                compatibility['warnings'].append("Firmware file is very small - may be corrupted")
            elif compatibility['file_size'] > 8 * 1024 * 1024:  # 8MB
                compatibility['warnings'].append("Firmware file is very large - may exceed flash capacity")
            
            # Basic compatibility check
            if compatibility['file_exists'] and file_ext in ['.bin', '.elf']:
                compatibility['compatible'] = True
            
        except Exception as e:
            compatibility['errors'].append(f"Error checking compatibility: {e}")
        
        return compatibility
    
    def backup_firmware(self, port: Optional[str] = None, 
                       backup_path: Optional[str] = None) -> Optional[str]:
        """
        Backup current firmware from ESP32.
        
        Args:
            port: Serial port (auto-detected if None)
            backup_path: Path to save backup (auto-generated if None)
            
        Returns:
            str: Path to backup file, or None if failed
        """
        try:
            if not port:
                devices = self.detect_mcu_devices()
                if not devices:
                    raise MCUFlashError("No ESP32 devices detected")
                port = devices[0].get('port', 'auto')
            
            if not backup_path:
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                backup_path = f"mcu_backup_{timestamp}.bin"
            
            self.logger.info(f"Backing up MCU firmware to: {backup_path}")
            
            # Read flash command
            cmd = self._build_esptool_cmd([
                '--port', port,
                '--baud', str(self.flash_config['baud_rate']),
                'read_flash',
                '0x0',  # Start address
                '0x400000',  # 4MB
                backup_path
            ])
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes
            )
            
            if result.returncode == 0:
                self.logger.info(f"MCU firmware backup completed: {backup_path}")
                return backup_path
            else:
                self.logger.error(f"MCU firmware backup failed: {result.stderr}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error backing up MCU firmware: {e}")
            return None
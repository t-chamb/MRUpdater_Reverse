# FPGA flashing workflow for Chromatic devices
# Implements openFPGALoader integration with progress monitoring and error detection

import os
import subprocess
import logging
import time
import re
from dataclasses import dataclass
from typing import Optional, Callable, Dict, Any, List
from pathlib import Path

from .util import get_openfpga_loader_bin_path
from .constants import CHROMATIC_VID, CHROMATIC_PID, GOWIN_VID, GOWIN_PID
from .device_communication import DeviceCommunicationManager
from .version_detector import FirmwareVersion

logger = logging.getLogger('mrupdater.fpga_flasher')

@dataclass
class FPGAFlashProgress:
    """FPGA flashing progress information"""
    stage: str
    progress_percent: float
    current_operation: str
    bytes_written: int = 0
    total_bytes: int = 0
    elapsed_time: float = 0.0
    estimated_remaining: Optional[float] = None

class FPGAFlashError(Exception):
    """Raised when FPGA flashing fails"""
    pass

class FPGADetectionError(Exception):
    """Raised when FPGA detection fails"""
    pass

class FPGAFlasher:
    """
    Handles FPGA bitstream flashing for Chromatic devices.
    
    Integrates with openFPGALoader for FPGA operations, provides progress monitoring,
    error detection, and verification after flashing.
    """
    
    def __init__(self, device_communicator: Optional[DeviceCommunicationManager] = None):
        self.device_communicator = device_communicator
        self.logger = logging.getLogger('mrupdater.fpga_flasher')
        
        # Get openFPGALoader binary path
        self.openfpga_loader_path = get_openfpga_loader_bin_path()
        if not self.openfpga_loader_path:
            raise FPGAFlashError("openFPGALoader binary not found")
        
        self.logger.info(f"Using openFPGALoader at: {self.openfpga_loader_path}")
    
    def detect_fpga_devices(self) -> List[Dict[str, Any]]:
        """
        Detect connected FPGA devices.
        
        Returns:
            List[Dict[str, Any]]: List of detected FPGA devices
        """
        try:
            self.logger.info("Detecting FPGA devices...")
            
            # Run openFPGALoader --detect
            cmd = [self.openfpga_loader_path, '--detect']
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                self.logger.error(f"FPGA detection failed: {result.stderr}")
                raise FPGADetectionError(f"Detection failed: {result.stderr}")
            
            # Parse detection output
            devices = self._parse_detection_output(result.stdout)
            
            self.logger.info(f"Detected {len(devices)} FPGA device(s)")
            for device in devices:
                self.logger.info(f"  - {device['name']} (Cable: {device.get('cable', 'unknown')})")
            
            return devices
            
        except subprocess.TimeoutExpired:
            self.logger.error("FPGA detection timed out")
            raise FPGADetectionError("Detection timed out")
        except Exception as e:
            self.logger.error(f"Error detecting FPGA devices: {e}")
            raise FPGADetectionError(f"Detection error: {e}")
    
    def _parse_detection_output(self, output: str) -> List[Dict[str, Any]]:
        """
        Parse openFPGALoader detection output.
        
        Args:
            output: Raw detection output
            
        Returns:
            List[Dict[str, Any]]: Parsed device information
        """
        devices = []
        
        try:
            lines = output.strip().split('\n')
            
            for line in lines:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                # Look for device information patterns
                # Example: "Jtag probe 0: gwu2x (0x33aa:0x0120)"
                device_match = re.search(r'Jtag probe (\d+):\s*(\w+)\s*\(([^)]+)\)', line)
                if device_match:
                    probe_id = device_match.group(1)
                    cable_name = device_match.group(2)
                    usb_info = device_match.group(3)
                    
                    device = {
                        'probe_id': int(probe_id),
                        'cable': cable_name,
                        'usb_info': usb_info,
                        'name': f"FPGA Device {probe_id}"
                    }
                    
                    # Extract VID:PID if available
                    vid_pid_match = re.search(r'0x([0-9a-fA-F]+):0x([0-9a-fA-F]+)', usb_info)
                    if vid_pid_match:
                        device['vid'] = int(vid_pid_match.group(1), 16)
                        device['pid'] = int(vid_pid_match.group(2), 16)
                    
                    devices.append(device)
                
                # Look for device chain information
                elif 'device(s) found' in line.lower():
                    # Extract device count and types
                    count_match = re.search(r'(\d+)\s+device\(s\)\s+found', line)
                    if count_match and devices:
                        # Update the last device with chain info
                        devices[-1]['chain_length'] = int(count_match.group(1))
        
        except Exception as e:
            self.logger.warning(f"Error parsing detection output: {e}")
        
        return devices
    
    def flash_fpga_bitstream(self, bitstream_path: str, 
                           cable: Optional[str] = None,
                           progress_callback: Optional[Callable[[FPGAFlashProgress], None]] = None) -> bool:
        """
        Flash FPGA bitstream to device.
        
        Args:
            bitstream_path: Path to FPGA bitstream file (.fs)
            cable: Cable type to use (auto-detected if None)
            progress_callback: Optional callback for progress updates
            
        Returns:
            bool: True if flashing succeeded
        """
        try:
            self.logger.info(f"Starting FPGA bitstream flash: {bitstream_path}")
            
            # Validate bitstream file
            if not os.path.exists(bitstream_path):
                raise FPGAFlashError(f"Bitstream file not found: {bitstream_path}")
            
            file_size = os.path.getsize(bitstream_path)
            self.logger.info(f"Bitstream file size: {file_size} bytes")
            
            # Detect cable if not specified
            if not cable:
                devices = self.detect_fpga_devices()
                if not devices:
                    raise FPGAFlashError("No FPGA devices detected")
                
                # Use first detected device
                cable = devices[0].get('cable', 'gwu2x')
                self.logger.info(f"Using auto-detected cable: {cable}")
            
            # Prepare flashing command
            cmd = [
                self.openfpga_loader_path,
                '--write-flash',
                '--cable', cable,
                '--reset',
                bitstream_path
            ]
            
            self.logger.info(f"Flashing command: {' '.join(cmd)}")
            
            # Start flashing process
            start_time = time.time()
            
            if progress_callback:
                progress_callback(FPGAFlashProgress(
                    stage="initializing",
                    progress_percent=0.0,
                    current_operation="Starting FPGA flash...",
                    total_bytes=file_size
                ))
            
            # Run flashing process with real-time output monitoring
            success = self._run_flash_process(cmd, file_size, progress_callback, start_time)
            
            if success:
                elapsed_time = time.time() - start_time
                self.logger.info(f"FPGA flashing completed successfully in {elapsed_time:.2f}s")
                
                if progress_callback:
                    progress_callback(FPGAFlashProgress(
                        stage="completed",
                        progress_percent=100.0,
                        current_operation="Flash completed successfully",
                        bytes_written=file_size,
                        total_bytes=file_size,
                        elapsed_time=elapsed_time
                    ))
                
                # Verify flashing if device communicator is available
                if self.device_communicator:
                    self._verify_fpga_flash()
                
                return True
            else:
                raise FPGAFlashError("FPGA flashing failed")
                
        except Exception as e:
            self.logger.error(f"FPGA flashing error: {e}")
            if progress_callback:
                progress_callback(FPGAFlashProgress(
                    stage="error",
                    progress_percent=0.0,
                    current_operation=f"Error: {e}"
                ))
            raise FPGAFlashError(f"FPGA flashing failed: {e}")
    
    def _run_flash_process(self, cmd: List[str], file_size: int,
                          progress_callback: Optional[Callable[[FPGAFlashProgress], None]],
                          start_time: float) -> bool:
        """
        Run the flashing process with progress monitoring.
        
        Args:
            cmd: Command to execute
            file_size: Size of bitstream file
            progress_callback: Progress callback function
            start_time: Start time for elapsed calculation
            
        Returns:
            bool: True if process succeeded
        """
        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            bytes_written = 0
            current_stage = "flashing"
            
            # Monitor process output
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                
                if output:
                    line = output.strip()
                    self.logger.debug(f"openFPGALoader: {line}")
                    
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
                            
                            progress_callback(FPGAFlashProgress(
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
                self.logger.info("openFPGALoader completed successfully")
                return True
            else:
                self.logger.error(f"openFPGALoader failed with return code {return_code}")
                return False
                
        except subprocess.TimeoutExpired:
            self.logger.error("FPGA flashing process timed out")
            process.kill()
            return False
        except Exception as e:
            self.logger.error(f"Error running flash process: {e}")
            return False
    
    def _parse_flash_output(self, line: str, file_size: int) -> Optional[Dict[str, Any]]:
        """
        Parse openFPGALoader output for progress information.
        
        Args:
            line: Output line from openFPGALoader
            file_size: Total file size for percentage calculation
            
        Returns:
            Dict[str, Any]: Parsed progress information, or None
        """
        progress_info = {}
        
        try:
            # Look for various progress indicators
            
            # Percentage progress: "Progress: 45%"
            percent_match = re.search(r'Progress:\s*(\d+)%', line, re.IGNORECASE)
            if percent_match:
                percent = int(percent_match.group(1))
                progress_info['bytes_written'] = int(file_size * percent / 100)
                progress_info['stage'] = 'flashing'
                return progress_info
            
            # Bytes written: "Written 12345 bytes"
            bytes_match = re.search(r'Written\s+(\d+)\s+bytes', line, re.IGNORECASE)
            if bytes_match:
                progress_info['bytes_written'] = int(bytes_match.group(1))
                progress_info['stage'] = 'flashing'
                return progress_info
            
            # Stage detection
            if 'erasing' in line.lower():
                progress_info['stage'] = 'erasing'
            elif 'programming' in line.lower() or 'writing' in line.lower():
                progress_info['stage'] = 'programming'
            elif 'verifying' in line.lower():
                progress_info['stage'] = 'verifying'
            elif 'resetting' in line.lower():
                progress_info['stage'] = 'resetting'
            
            if progress_info:
                return progress_info
                
        except Exception as e:
            self.logger.debug(f"Error parsing flash output: {e}")
        
        return None
    
    def _verify_fpga_flash(self) -> bool:
        """
        Verify FPGA flash by checking device communication.
        
        Returns:
            bool: True if verification succeeded
        """
        try:
            self.logger.info("Verifying FPGA flash...")
            
            # Wait for device to reset and come back online
            time.sleep(2.0)
            
            # Try to establish communication
            if not self.device_communicator.connect():
                self.logger.warning("Could not establish communication after FPGA flash")
                return False
            
            # Query device version to verify FPGA is responding
            from .version_detector import VersionDetector
            version_detector = VersionDetector(self.device_communicator.transport)
            
            device_version = version_detector.get_device_version(timeout=10.0)
            if device_version:
                self.logger.info(f"FPGA flash verification successful - FPGA version: {device_version.fpga_version}")
                return True
            else:
                self.logger.warning("Could not query device version after FPGA flash")
                return False
                
        except Exception as e:
            self.logger.warning(f"FPGA flash verification failed: {e}")
            return False
    
    def get_fpga_info(self) -> Optional[Dict[str, Any]]:
        """
        Get FPGA device information.
        
        Returns:
            Dict[str, Any]: FPGA device information, or None if failed
        """
        try:
            devices = self.detect_fpga_devices()
            if not devices:
                return None
            
            # Return information about the first device
            device = devices[0]
            
            # Add additional info if device communicator is available
            if self.device_communicator and self.device_communicator.is_connected():
                try:
                    from .version_detector import VersionDetector
                    version_detector = VersionDetector(self.device_communicator.transport)
                    
                    device_version = version_detector.get_device_version()
                    if device_version:
                        device['fpga_version'] = device_version.fpga_version
                        device['mcu_version'] = device_version.mcu_version
                        
                except Exception as e:
                    self.logger.debug(f"Could not get device version: {e}")
            
            return device
            
        except Exception as e:
            self.logger.error(f"Error getting FPGA info: {e}")
            return None
    
    def reset_fpga(self, cable: Optional[str] = None) -> bool:
        """
        Reset FPGA device.
        
        Args:
            cable: Cable type to use (auto-detected if None)
            
        Returns:
            bool: True if reset succeeded
        """
        try:
            self.logger.info("Resetting FPGA device...")
            
            # Detect cable if not specified
            if not cable:
                devices = self.detect_fpga_devices()
                if not devices:
                    raise FPGAFlashError("No FPGA devices detected")
                
                cable = devices[0].get('cable', 'gwu2x')
            
            # Reset command
            cmd = [
                self.openfpga_loader_path,
                '--cable', cable,
                '--reset'
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                self.logger.info("FPGA reset completed successfully")
                return True
            else:
                self.logger.error(f"FPGA reset failed: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error resetting FPGA: {e}")
            return False
    
    def check_fpga_compatibility(self, bitstream_path: str) -> Dict[str, Any]:
        """
        Check FPGA bitstream compatibility.
        
        Args:
            bitstream_path: Path to bitstream file
            
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
            if not os.path.exists(bitstream_path):
                compatibility['errors'].append(f"Bitstream file not found: {bitstream_path}")
                return compatibility
            
            compatibility['file_exists'] = True
            compatibility['file_size'] = os.path.getsize(bitstream_path)
            
            # Check file extension
            file_ext = Path(bitstream_path).suffix.lower()
            if file_ext == '.fs':
                compatibility['file_format'] = 'Gowin bitstream'
            elif file_ext == '.bit':
                compatibility['file_format'] = 'Xilinx bitstream'
                compatibility['warnings'].append("Xilinx bitstream format detected - may not be compatible with Gowin FPGA")
            else:
                compatibility['warnings'].append(f"Unknown bitstream format: {file_ext}")
            
            # Check file size (typical Gowin bitstreams are 1-10MB)
            if compatibility['file_size'] < 1000:
                compatibility['warnings'].append("Bitstream file is very small - may be corrupted")
            elif compatibility['file_size'] > 50 * 1024 * 1024:  # 50MB
                compatibility['warnings'].append("Bitstream file is very large - may not be compatible")
            
            # Basic compatibility check
            if compatibility['file_exists'] and file_ext == '.fs':
                compatibility['compatible'] = True
            
        except Exception as e:
            compatibility['errors'].append(f"Error checking compatibility: {e}")
        
        return compatibility
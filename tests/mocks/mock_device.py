#!/usr/bin/env python3
"""
Mock device classes for testing without hardware.
Provides mock implementations of Chromatic device communication.
"""

import time
import json
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from unittest.mock import Mock

from libpyretro.cartclinic.comms.transport import ResponseMessage, CommandMessage
from flashing_tool.device_manager import DeviceInfo


@dataclass
class MockCartridgeData:
    """Mock cartridge data for testing"""
    title: str = "TEST ROM"
    cartridge_type: int = 0x00  # ROM only
    rom_size: int = 0x00  # 32KB
    ram_size: int = 0x00  # No RAM
    header_checksum: int = 0x43
    global_checksum: int = 0x991C
    rom_data: bytes = b'\x00' * (32 * 1024)  # 32KB of zeros
    
    def get_header_bytes(self) -> bytes:
        """Generate mock cartridge header"""
        header = bytearray(0x50)  # Header is 0x100-0x14F
        
        # Entry point (0x100-0x103)
        header[0x00:0x04] = b'\x00\xC3\x50\x01'
        
        # Nintendo logo (0x104-0x133) - simplified
        header[0x04:0x34] = b'\xCE\xED\x66\x66' + b'\x00' * 44
        
        # Title (0x134-0x143)
        title_bytes = self.title.encode('ascii')[:16]
        header[0x34:0x34+len(title_bytes)] = title_bytes
        
        # Cartridge type (0x147)
        header[0x47] = self.cartridge_type
        
        # ROM size (0x148)
        header[0x48] = self.rom_size
        
        # RAM size (0x149)
        header[0x49] = self.ram_size
        
        # Header checksum (0x14D)
        header[0x4D] = self.header_checksum
        
        # Global checksum (0x14E-0x14F)
        header[0x4E:0x50] = self.global_checksum.to_bytes(2, 'big')
        
        return bytes(header)


class MockSerialTransport:
    """Mock serial transport for testing device communication"""
    
    def __init__(self, port: str = "/dev/mock", simulate_errors: bool = False):
        self.port = port
        self.connected = False
        self.simulate_errors = simulate_errors
        self.command_count = 0
        self.cartridge_data = MockCartridgeData()
        self.firmware_version = {
            'mcu_version': '1.0.0',
            'fpga_version': '1.0.0',
            'build_date': '2024-01-01'
        }
        
    def connect(self, timeout: float = 5.0) -> bool:
        """Mock connection"""
        if self.simulate_errors and self.command_count % 10 == 9:
            return False
        self.connected = True
        return True
        
    def disconnect(self):
        """Mock disconnection"""
        self.connected = False
        
    def is_connected(self) -> bool:
        """Check mock connection status"""
        return self.connected
        
    def ping(self) -> bool:
        """Mock ping command"""
        if not self.connected:
            return False
        return not (self.simulate_errors and self.command_count % 20 == 19)
        
    def send_command(self, command: CommandMessage) -> ResponseMessage:
        """Mock command sending with realistic responses"""
        self.command_count += 1
        
        if not self.connected:
            return ResponseMessage(
                success=False,
                error="Device not connected"
            )
            
        # Simulate occasional errors
        if self.simulate_errors and self.command_count % 15 == 14:
            return ResponseMessage(
                success=False,
                error="Communication timeout"
            )
            
        # Handle different command types
        if command.command == "ping":
            return ResponseMessage(success=True, data={"pong": True})
            
        elif command.command == "get_version":
            return ResponseMessage(
                success=True,
                data=self.firmware_version
            )
            
        elif command.command == "cart_detect":
            # Simulate cartridge detection
            return ResponseMessage(
                success=True,
                data={
                    'inserted': True,
                    'raw_response': b'\x01\x00\x00'
                }
            )
            
        elif command.command == "cart_read_header":
            # Return mock cartridge header
            header_data = self.cartridge_data.get_header_bytes()
            return ResponseMessage(
                success=True,
                data={
                    'header_data': header_data.hex(),
                    'length': len(header_data)
                }
            )
            
        elif command.command == "cart_read_rom":
            # Mock ROM reading
            start_addr = command.params.get('start_address', 0)
            length = command.params.get('length', 1024)
            
            # Simulate reading from ROM data
            end_addr = min(start_addr + length, len(self.cartridge_data.rom_data))
            rom_chunk = self.cartridge_data.rom_data[start_addr:end_addr]
            
            return ResponseMessage(
                success=True,
                data={
                    'rom_data': rom_chunk.hex(),
                    'address': start_addr,
                    'length': len(rom_chunk)
                }
            )
            
        elif command.command == "cart_write_rom":
            # Mock ROM writing
            return ResponseMessage(
                success=True,
                data={'bytes_written': command.params.get('length', 0)}
            )
            
        elif command.command == "flash_fpga":
            # Mock FPGA flashing
            time.sleep(0.1)  # Simulate flash time
            return ResponseMessage(
                success=True,
                data={'flash_complete': True}
            )
            
        elif command.command == "flash_mcu":
            # Mock MCU flashing
            time.sleep(0.1)  # Simulate flash time
            return ResponseMessage(
                success=True,
                data={'flash_complete': True}
            )
            
        else:
            return ResponseMessage(
                success=False,
                error=f"Unknown command: {command.command}"
            )


class MockDeviceManager:
    """Mock device manager for testing device detection"""
    
    def __init__(self, device_count: int = 1, simulate_no_devices: bool = False):
        self.device_count = device_count if not simulate_no_devices else 0
        self.simulate_no_devices = simulate_no_devices
        
    def scan_for_devices(self) -> List[DeviceInfo]:
        """Mock device scanning"""
        if self.simulate_no_devices:
            return []
            
        devices = []
        for i in range(self.device_count):
            device = DeviceInfo(
                serial_port=f"/dev/mock{i}",
                usb_path=f"mock_usb_path_{i}",
                serial_number=f"MOCK{i:04d}",
                product_name="Mock Chromatic Device",
                manufacturer="Mock ModRetro"
            )
            devices.append(device)
            
        return devices
        
    def get_device_info(self, port: str) -> Optional[DeviceInfo]:
        """Get mock device info"""
        if self.simulate_no_devices:
            return None
            
        return DeviceInfo(
            serial_port=port,
            usb_path="mock_usb_path",
            serial_number="MOCK0001",
            product_name="Mock Chromatic Device",
            manufacturer="Mock ModRetro"
        )


class MockFirmwareManager:
    """Mock firmware manager for testing firmware operations"""
    
    def __init__(self, simulate_network_error: bool = False):
        self.simulate_network_error = simulate_network_error
        self.mock_manifest = {
            'latest_version': '2.0.0',
            'firmware_list': [
                {
                    'version': '2.0.0',
                    'mcu_binary_key': 'firmware/v2.0.0/mcu.bin',
                    'fpga_bitstream_key': 'firmware/v2.0.0/fpga.fs',
                    'changelog': 'Latest improvements',
                    'release_date': '2024-01-15'
                },
                {
                    'version': '1.9.0',
                    'mcu_binary_key': 'firmware/v1.9.0/mcu.bin',
                    'fpga_bitstream_key': 'firmware/v1.9.0/fpga.fs',
                    'changelog': 'Bug fixes',
                    'release_date': '2024-01-01'
                }
            ]
        }
        
    def get_firmware_manifest(self) -> Optional[Dict[str, Any]]:
        """Mock firmware manifest retrieval"""
        if self.simulate_network_error:
            return None
        return self.mock_manifest
        
    def download_firmware(self, version: str) -> bool:
        """Mock firmware download"""
        if self.simulate_network_error:
            return False
        time.sleep(0.1)  # Simulate download time
        return True
        
    def list_cached_versions(self) -> List[str]:
        """Mock cached versions list"""
        return ['1.9.0', '1.8.0']
        
    def get_cache_size(self) -> int:
        """Mock cache size"""
        return 1024 * 1024 * 50  # 50MB


class MockProgressCallback:
    """Mock progress callback for testing progress reporting"""
    
    def __init__(self):
        self.progress_updates = []
        self.completed = False
        self.error = None
        
    def __call__(self, progress_data: Dict[str, Any]):
        """Record progress updates"""
        self.progress_updates.append(progress_data.copy())
        
        if progress_data.get('stage') == 'complete':
            self.completed = True
        elif progress_data.get('error'):
            self.error = progress_data['error']
            
    def get_last_progress(self) -> Optional[Dict[str, Any]]:
        """Get the last progress update"""
        return self.progress_updates[-1] if self.progress_updates else None
        
    def get_progress_count(self) -> int:
        """Get number of progress updates received"""
        return len(self.progress_updates)
        
    def reset(self):
        """Reset progress tracking"""
        self.progress_updates.clear()
        self.completed = False
        self.error = None
#!/usr/bin/env python3
"""
Mock Chromatic device that responds to protocol commands.
Provides realistic device simulation for integration testing.
"""

import time
import json
import threading
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from enum import Enum

from libpyretro.cartclinic.comms.transport import ResponseMessage, CommandMessage
from cartclinic.cartridge_info import CartridgeInfo
from tests.mocks.mock_device import MockCartridgeData


class DeviceState(Enum):
    """Mock device states"""
    DISCONNECTED = "disconnected"
    CONNECTED = "connected"
    FLASHING_FPGA = "flashing_fpga"
    FLASHING_MCU = "flashing_mcu"
    READING_CARTRIDGE = "reading_cartridge"
    WRITING_CARTRIDGE = "writing_cartridge"
    ERROR = "error"


@dataclass
class MockDeviceConfig:
    """Configuration for mock device behavior"""
    # Device identification
    serial_number: str = "MOCK001"
    product_name: str = "Mock Chromatic Device"
    manufacturer: str = "Mock ModRetro"
    
    # Firmware versions
    mcu_version: str = "1.9.0"
    fpga_version: str = "1.9.0"
    build_date: str = "2024-01-01"
    
    # Behavior simulation
    simulate_errors: bool = False
    error_probability: float = 0.1  # 10% chance of errors
    response_delay: float = 0.01    # 10ms response delay
    flash_duration: float = 2.0     # 2 second flash simulation
    
    # Cartridge simulation
    cartridge_inserted: bool = True
    cartridge_data: MockCartridgeData = field(default_factory=MockCartridgeData)


class MockChromaticDevice:
    """
    Mock Chromatic device that responds to protocol commands.
    Simulates realistic device behavior for integration testing.
    """
    
    def __init__(self, config: MockDeviceConfig = None):
        self.config = config or MockDeviceConfig()
        self.state = DeviceState.DISCONNECTED
        self.command_history: List[CommandMessage] = []
        self.response_callbacks: Dict[str, Callable] = {}
        
        # Flash progress simulation
        self.flash_progress = 0.0
        self.flash_thread: Optional[threading.Thread] = None
        
        # Error simulation
        self.error_count = 0
        self.last_error: Optional[str] = None
        
    def connect(self) -> bool:
        """Simulate device connection"""
        if self.config.simulate_errors and self._should_simulate_error():
            self.last_error = "Connection failed"
            return False
            
        self.state = DeviceState.CONNECTED
        return True
        
    def disconnect(self):
        """Simulate device disconnection"""
        self.state = DeviceState.DISCONNECTED
        if self.flash_thread and self.flash_thread.is_alive():
            self.flash_thread.join(timeout=1.0)
            
    def is_connected(self) -> bool:
        """Check if device is connected"""
        return self.state != DeviceState.DISCONNECTED
        
    def send_command(self, command: CommandMessage) -> ResponseMessage:
        """Process command and return response"""
        self.command_history.append(command)
        
        # Simulate response delay
        if self.config.response_delay > 0:
            time.sleep(self.config.response_delay)
            
        # Check if device is connected
        if not self.is_connected():
            return ResponseMessage(
                success=False,
                error="Device not connected"
            )
            
        # Simulate random errors
        if self.config.simulate_errors and self._should_simulate_error():
            self.error_count += 1
            return ResponseMessage(
                success=False,
                error=f"Simulated error #{self.error_count}"
            )
            
        # Route command to appropriate handler
        handler_name = f"_handle_{command.command}"
        if hasattr(self, handler_name):
            handler = getattr(self, handler_name)
            return handler(command)
        else:
            return ResponseMessage(
                success=False,
                error=f"Unknown command: {command.command}"
            )
            
    def _should_simulate_error(self) -> bool:
        """Determine if an error should be simulated"""
        import random
        return random.random() < self.config.error_probability
        
    def _handle_ping(self, command: CommandMessage) -> ResponseMessage:
        """Handle ping command"""
        return ResponseMessage(
            success=True,
            data={"pong": True, "timestamp": time.time()}
        )
        
    def _handle_get_version(self, command: CommandMessage) -> ResponseMessage:
        """Handle version query"""
        return ResponseMessage(
            success=True,
            data={
                "mcu_version": self.config.mcu_version,
                "fpga_version": self.config.fpga_version,
                "build_date": self.config.build_date,
                "serial_number": self.config.serial_number
            }
        )
        
    def _handle_get_device_info(self, command: CommandMessage) -> ResponseMessage:
        """Handle device info query"""
        return ResponseMessage(
            success=True,
            data={
                "product_name": self.config.product_name,
                "manufacturer": self.config.manufacturer,
                "serial_number": self.config.serial_number,
                "usb_vid": "0x374E",
                "usb_pid": "0x013F"
            }
        )
        
    def _handle_cart_detect(self, command: CommandMessage) -> ResponseMessage:
        """Handle cartridge detection"""
        return ResponseMessage(
            success=True,
            data={
                "inserted": self.config.cartridge_inserted,
                "raw_response": b'\x01\x00\x00' if self.config.cartridge_inserted else b'\x00\x00\x00'
            }
        )
        
    def _handle_cart_read_header(self, command: CommandMessage) -> ResponseMessage:
        """Handle cartridge header reading"""
        if not self.config.cartridge_inserted:
            return ResponseMessage(
                success=False,
                error="No cartridge inserted"
            )
            
        self.state = DeviceState.READING_CARTRIDGE
        
        try:
            header_data = self.config.cartridge_data.get_header_bytes()
            return ResponseMessage(
                success=True,
                data={
                    "header_data": header_data.hex(),
                    "length": len(header_data)
                }
            )
        finally:
            self.state = DeviceState.CONNECTED
            
    def _handle_cart_read_rom(self, command: CommandMessage) -> ResponseMessage:
        """Handle ROM reading"""
        if not self.config.cartridge_inserted:
            return ResponseMessage(
                success=False,
                error="No cartridge inserted"
            )
            
        start_addr = command.params.get('start_address', 0)
        length = command.params.get('length', 1024)
        
        self.state = DeviceState.READING_CARTRIDGE
        
        try:
            # Simulate reading from ROM data
            rom_data = self.config.cartridge_data.rom_data
            end_addr = min(start_addr + length, len(rom_data))
            rom_chunk = rom_data[start_addr:end_addr]
            
            return ResponseMessage(
                success=True,
                data={
                    "rom_data": rom_chunk.hex(),
                    "address": start_addr,
                    "length": len(rom_chunk)
                }
            )
        finally:
            self.state = DeviceState.CONNECTED
            
    def _handle_cart_write_rom(self, command: CommandMessage) -> ResponseMessage:
        """Handle ROM writing"""
        if not self.config.cartridge_inserted:
            return ResponseMessage(
                success=False,
                error="No cartridge inserted"
            )
            
        start_addr = command.params.get('start_address', 0)
        rom_data = bytes.fromhex(command.params.get('rom_data', ''))
        
        self.state = DeviceState.WRITING_CARTRIDGE
        
        try:
            # Simulate write delay
            time.sleep(len(rom_data) / 10000)  # Simulate write speed
            
            return ResponseMessage(
                success=True,
                data={
                    "bytes_written": len(rom_data),
                    "address": start_addr
                }
            )
        finally:
            self.state = DeviceState.CONNECTED
            
    def _handle_flash_fpga(self, command: CommandMessage) -> ResponseMessage:
        """Handle FPGA flashing"""
        bitstream_data = command.params.get('bitstream_data', '')
        
        if not bitstream_data:
            return ResponseMessage(
                success=False,
                error="No bitstream data provided"
            )
            
        # Start flash simulation in background
        self.state = DeviceState.FLASHING_FPGA
        self.flash_progress = 0.0
        
        def flash_simulation():
            steps = 20
            for i in range(steps + 1):
                if self.state != DeviceState.FLASHING_FPGA:
                    break
                self.flash_progress = (i / steps) * 100
                time.sleep(self.config.flash_duration / steps)
                
            if self.state == DeviceState.FLASHING_FPGA:
                self.state = DeviceState.CONNECTED
                
        self.flash_thread = threading.Thread(target=flash_simulation)
        self.flash_thread.start()
        
        return ResponseMessage(
            success=True,
            data={"flash_started": True}
        )
        
    def _handle_flash_mcu(self, command: CommandMessage) -> ResponseMessage:
        """Handle MCU flashing"""
        binary_data = command.params.get('binary_data', '')
        
        if not binary_data:
            return ResponseMessage(
                success=False,
                error="No binary data provided"
            )
            
        # Start flash simulation in background
        self.state = DeviceState.FLASHING_MCU
        self.flash_progress = 0.0
        
        def flash_simulation():
            steps = 15
            for i in range(steps + 1):
                if self.state != DeviceState.FLASHING_MCU:
                    break
                self.flash_progress = (i / steps) * 100
                time.sleep(self.config.flash_duration / steps)
                
            if self.state == DeviceState.FLASHING_MCU:
                self.state = DeviceState.CONNECTED
                
        self.flash_thread = threading.Thread(target=flash_simulation)
        self.flash_thread.start()
        
        return ResponseMessage(
            success=True,
            data={"flash_started": True}
        )
        
    def _handle_get_flash_progress(self, command: CommandMessage) -> ResponseMessage:
        """Handle flash progress query"""
        return ResponseMessage(
            success=True,
            data={
                "progress": self.flash_progress,
                "state": self.state.value,
                "complete": self.state == DeviceState.CONNECTED
            }
        )
        
    def _handle_cancel_operation(self, command: CommandMessage) -> ResponseMessage:
        """Handle operation cancellation"""
        if self.state in [DeviceState.FLASHING_FPGA, DeviceState.FLASHING_MCU]:
            self.state = DeviceState.CONNECTED
            if self.flash_thread:
                # Thread will detect state change and exit
                pass
                
        return ResponseMessage(
            success=True,
            data={"cancelled": True}
        )
        
    def get_command_history(self) -> List[CommandMessage]:
        """Get history of commands sent to device"""
        return self.command_history.copy()
        
    def clear_command_history(self):
        """Clear command history"""
        self.command_history.clear()
        
    def set_cartridge_data(self, cartridge_data: MockCartridgeData):
        """Set cartridge data for simulation"""
        self.config.cartridge_data = cartridge_data
        
    def insert_cartridge(self, cartridge_data: MockCartridgeData = None):
        """Simulate cartridge insertion"""
        if cartridge_data:
            self.config.cartridge_data = cartridge_data
        self.config.cartridge_inserted = True
        
    def remove_cartridge(self):
        """Simulate cartridge removal"""
        self.config.cartridge_inserted = False
        
    def simulate_error_condition(self, error_message: str):
        """Force an error condition for testing"""
        self.state = DeviceState.ERROR
        self.last_error = error_message
        
    def reset_to_normal(self):
        """Reset device to normal operation"""
        self.state = DeviceState.CONNECTED
        self.last_error = None
        self.error_count = 0
# Manually reconstructed from bytecode analysis and context
# Source: libpyretro/cartclinic/comms/session.pyc

import logging
import time
import serial
from typing import Optional, List, Any, Dict
from .exceptions import WriteBlockDataError
from .transport import SerialTransport

class Transport:
    """Simple transport wrapper for backward compatibility"""
    
    def __init__(self):
        self.serial_transport = None
        
    def connect(self, port: str, baudrate: int = 115200, timeout: float = 1.0) -> bool:
        """Connect to device"""
        try:
            self.serial_transport = SerialTransport(port, baudrate, timeout)
            return self.serial_transport.connect()
        except Exception as e:
            logger.error(f"Transport connection failed: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from device"""
        if self.serial_transport:
            self.serial_transport.disconnect()
    
    def is_connected(self) -> bool:
        """Check if connected"""
        return self.serial_transport and self.serial_transport.is_connected()
    
    def send_command(self, command: bytes) -> bytes:
        """Send raw command bytes and return response"""
        if not self.is_connected():
            raise RuntimeError("Not connected")
        
        # Use the improved serial transport
        return self.serial_transport.send_command(command)
from ..cart_api import CartAPI_Builder, CartAPI_Parser

logger = logging.getLogger(__name__)

class Session:
    """Cart Clinic communication session"""
    
    def __init__(self, transport: Optional[Transport] = None):
        self.transport = transport
        self._connected = False
        self._cartridge_info = None
        
    def connect(self, port: str, baudrate: int = 115200, timeout: float = 1.0) -> bool:
        """Connect to the device"""
        try:
            if self.transport is None:
                self.transport = Transport()
            
            self._connected = self.transport.connect(port, baudrate, timeout)
            return self._connected
        except Exception as e:
            logger.error(f"Failed to connect: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from the device"""
        if self.transport:
            self.transport.disconnect()
        self._connected = False
    
    def is_connected(self) -> bool:
        """Check if connected"""
        return self._connected and self.transport and self.transport.is_connected()
    
    def send_command(self, command: bytes) -> bytes:
        """Send a command and get response"""
        if not self.is_connected():
            raise RuntimeError("Not connected")
        
        return self.transport.send_command(command)
    
    def get_cartridge_info(self) -> Optional[Dict]:
        """Get cartridge information"""
        if self._cartridge_info:
            return self._cartridge_info
            
        try:
            # Detect cartridge presence with retry logic
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    detect_cmd = CartAPI_Builder.detect_cart()
                    logger.debug(f"Sending detect command (attempt {attempt + 1}): {detect_cmd.hex()}")
                    
                    response = self.send_command(detect_cmd)
                    logger.debug(f"Detect response: {response.hex() if response else 'None'}")
                    
                    if not response:
                        logger.warning("No response received")
                        if attempt < max_retries - 1:
                            time.sleep(0.1)
                            continue
                        else:
                            raise RuntimeError("No response from device")
                    
                    # Handle the correct 4-byte response format
                    if len(response) >= 4:
                        # Standard 4-byte response
                        if response[0] != 5:  # DetectCart command ID
                            logger.error(f"Unexpected CmdId {response[0]}. Expecting 5")
                            if attempt < max_retries - 1:
                                time.sleep(0.1)
                                continue
                            else:
                                raise RuntimeError(f"Protocol error: got command ID {response[0]}, expected 5")
                        
                        # Parse the response: [cmd_id, status, 0, 0]
                        # Status byte: bit 0 = inserted, bit 1 = removed
                        status_byte = response[1]
                        inserted = (status_byte & 0x01) != 0
                        removed = (status_byte & 0x02) != 0
                        
                        logger.info(f"Cartridge detection: status=0x{status_byte:02X}, inserted={inserted}, removed={removed}")
                        
                    else:
                        # Invalid response length
                        logger.warning(f"Invalid detect response length: {len(response)}")
                        if attempt < max_retries - 1:
                            time.sleep(0.1)
                            continue
                        else:
                            raise RuntimeError("Invalid response format")
                    
                    if not inserted:
                        logger.warning("No cartridge detected")
                        return None
                    
                    break  # Success, exit retry loop
                    
                except Exception as e:
                    logger.error(f"Detect attempt {attempt + 1} failed: {e}")
                    if attempt == max_retries - 1:
                        raise
                    time.sleep(0.1)
            
            # Read cartridge header to get size information
            header_data = self.read_header()
            if not header_data:
                logger.error("Failed to read cartridge header")
                return None
            
            # Parse header to get ROM size
            from cartclinic.cartridge_info import CartridgeInfo
            cartridge_info = CartridgeInfo.from_header_data(header_data)
            
            self._cartridge_info = {
                'rom_size': cartridge_info.rom_size_bytes,
                'rom_banks': cartridge_info.rom_banks,
                'ram_size': cartridge_info.ram_size_bytes,
                'ram_banks': cartridge_info.ram_banks,
                'title': cartridge_info.header.title,
                'mapper': cartridge_info.mapper_name,
                'has_battery': cartridge_info.has_battery,
                'has_ram': cartridge_info.has_ram
            }
            
            return self._cartridge_info
            
        except Exception as e:
            logger.error(f"Failed to get cartridge info: {e}")
            return None
    
    def read_header(self) -> Optional[bytes]:
        """Read cartridge header (first 0x150 bytes)"""
        try:
            header_data = bytearray()
            
            # Read header data byte by byte
            for addr in range(0x150):
                block = addr // 256
                offset = addr % 256
                bank_index = 0  # Header is always in bank 0
                
                read_cmd = CartAPI_Builder.read_byte(block, offset, bank_index)
                response = self.send_command(read_cmd)
                
                if not response or len(response) < 4:
                    logger.error(f"Invalid response for address 0x{addr:04X}")
                    return None
                
                if response[0] != 2:  # ReadCartByte command ID
                    logger.error(f"Unexpected command ID {response[0]} for read at 0x{addr:04X}")
                    return None
                
                # Parse response: [cmd_id, addr_low, addr_high, data_byte]
                resp_addr = response[1] | (response[2] << 8)
                data_byte = response[3]
                
                if resp_addr != addr:
                    logger.warning(f"Address mismatch: requested 0x{addr:04X}, got 0x{resp_addr:04X}")
                
                header_data.append(data_byte)
                
                # Small delay to avoid overwhelming the device
                if addr % 16 == 0:
                    time.sleep(0.001)
            
            return bytes(header_data)
            
        except Exception as e:
            logger.error(f"Failed to read header: {e}")
            return None
    
    def read_bank(self, bank_num: int) -> Optional[bytes]:
        """Read a single 16KB bank from cartridge"""
        try:
            bank_data = bytearray()
            bank_size = 16384  # 16KB per bank
            
            # Set the bank if needed (for banks > 1)
            if bank_num > 1:
                set_bank_cmds = CartAPI_Builder.set_bank(bank_num)
                for cmd in set_bank_cmds:
                    self.send_command(cmd)
            
            # Read bank data
            for addr in range(bank_size):
                block = addr // 256
                offset = addr % 256
                bank_index = 1 if bank_num > 0 else 0  # Use bank 1 for switchable banks
                
                read_cmd = CartAPI_Builder.read_byte(block, offset, bank_index)
                response = self.send_command(read_cmd)
                addr_read, data_byte = CartAPI_Parser.byte_read(response)
                
                bank_data.append(data_byte)
            
            return bytes(bank_data)
            
        except Exception as e:
            logger.error(f"Failed to read bank {bank_num}: {e}")
            return None
    
    def read_save_data(self) -> Optional[bytes]:
        """Read save data from cartridge RAM"""
        try:
            cartridge_info = self.get_cartridge_info()
            if not cartridge_info or not cartridge_info.get('has_ram'):
                logger.warning("Cartridge has no save RAM")
                return None
            
            ram_size = cartridge_info.get('ram_size', 0)
            if ram_size == 0:
                return None
            
            # Enable RAM access
            enable_cmd = CartAPI_Builder.enable_ram()
            self.send_command(enable_cmd)
            
            save_data = bytearray()
            
            # Read RAM data
            for addr in range(ram_size):
                block = (addr // 256) + 0xA0  # RAM starts at 0xA000
                offset = addr % 256
                
                read_cmd = CartAPI_Builder.read_byte_fram(block - 0xA0, offset)
                response = self.send_command(read_cmd)
                addr_read, data_byte = CartAPI_Parser.byte_read(response)
                
                save_data.append(data_byte)
            
            # Disable RAM access
            disable_cmd = CartAPI_Builder.disable_ram()
            self.send_command(disable_cmd)
            
            return bytes(save_data)
            
        except Exception as e:
            logger.error(f"Failed to read save data: {e}")
            return None
    
    def write_block_data(self, address: int, data: bytes) -> bool:
        """Write block data to device"""
        try:
            # Implementation based on bytecode analysis
            if not self.is_connected():
                raise WriteBlockDataError("Not connected")
            
            # Send write command with address and data
            command = self._build_write_command(address, data)
            response = self.send_command(command)
            
            return self._validate_write_response(response)
            
        except Exception as e:
            logger.error(f"Write block data failed: {e}")
            raise WriteBlockDataError(f"Write failed: {e}")
    
    def _build_write_command(self, address: int, data: bytes) -> bytes:
        """Build write command packet"""
        # Based on protocol analysis
        cmd_header = b'\x02'  # Write command
        addr_bytes = address.to_bytes(4, 'little')
        length_bytes = len(data).to_bytes(2, 'little')
        
        return cmd_header + addr_bytes + length_bytes + data
    
    def _validate_write_response(self, response: bytes) -> bool:
        """Validate write response"""
        if len(response) < 1:
            return False
        
        return response[0] == 0x00  # Success response
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()
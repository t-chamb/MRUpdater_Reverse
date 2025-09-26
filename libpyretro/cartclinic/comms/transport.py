"""
Serial transport layer for Cart Clinic communication
"""

import logging
import serial
import time
from typing import Optional, Dict, Any
from enum import Enum
from dataclasses import dataclass

logger = logging.getLogger(__name__)

class TransportKind(Enum):
    """Transport type enumeration"""
    SERIAL = "serial"
    USB = "usb"

class CommandType(Enum):
    """Command type enumeration"""
    DETECT_CART = 5
    READ_BYTE = 2
    WRITE_BYTE = 3
    SET_BANK = 100  # Custom command type

@dataclass
class CommandProperty:
    """Command property descriptor"""
    name: str
    value: Any
    required: bool = True

@dataclass
class CommandMessage:
    """Command message structure"""
    command_type: CommandType
    payload: bytes
    properties: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.properties is None:
            self.properties = {}

@dataclass
class ResponseMessage:
    """Response message structure"""
    command_id: int
    payload: bytes
    success: bool = True
    error_message: str = ""

class SessionManager:
    """Session manager for device communication"""
    
    def __init__(self):
        self.active_sessions = {}
        self.transport_instances = {}
    
    def create_session(self, transport_kind: TransportKind, **kwargs) -> 'Session':
        """Create a new communication session"""
        if transport_kind == TransportKind.SERIAL:
            transport = SerialTransport(**kwargs)
            # Import here to avoid circular imports
            from .session import Session
            return Session(transport)
        else:
            raise ValueError(f"Unsupported transport kind: {transport_kind}")
    
    def get_session(self, session_id: str) -> Optional['Session']:
        """Get an existing session by ID"""
        return self.active_sessions.get(session_id)
    
    def register_session(self, session_id: str, session: 'Session'):
        """Register a session"""
        self.active_sessions[session_id] = session
    
    def unregister_session(self, session_id: str):
        """Unregister a session"""
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]

class SerialTransport:
    """Serial transport for communicating with Chromatic device"""
    
    def __init__(self, port: str, baudrate: int = 115200, timeout: float = 1.0):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial_conn: Optional[serial.Serial] = None
        
    def connect(self) -> bool:
        """Connect to the serial port"""
        try:
            self.serial_conn = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE
            )
            
            if self.serial_conn.is_open:
                logger.info(f"Connected to {self.port} at {self.baudrate} baud")
                # Give the device a moment to initialize
                time.sleep(0.1)
                return True
            else:
                logger.error(f"Failed to open {self.port}")
                return False
                
        except Exception as e:
            logger.error(f"Serial connection failed: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from the serial port"""
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.close()
            logger.info(f"Disconnected from {self.port}")
        self.serial_conn = None
    
    def is_connected(self) -> bool:
        """Check if connected"""
        return self.serial_conn is not None and self.serial_conn.is_open
    
    def send_command(self, command: bytes) -> bytes:
        """Send command and receive response"""
        if not self.is_connected():
            raise RuntimeError("Not connected to device")
        
        try:
            # Clear any pending data
            self.serial_conn.reset_input_buffer()
            
            # Send command
            logger.debug(f"Sending command: {command.hex()}")
            bytes_written = self.serial_conn.write(command)
            self.serial_conn.flush()
            
            if bytes_written != len(command):
                logger.warning(f"Only wrote {bytes_written}/{len(command)} bytes")
            
            # Wait for response with adaptive timeout
            time.sleep(0.05)  # Longer delay for device processing
            
            # Read response with more flexible approach
            response = bytearray()
            max_wait_time = 1.0  # Maximum wait time in seconds
            start_time = time.time()
            
            # First, try to get at least one byte
            while len(response) == 0 and (time.time() - start_time) < max_wait_time:
                if self.serial_conn.in_waiting > 0:
                    chunk = self.serial_conn.read(1)  # Read one byte at a time
                    response.extend(chunk)
                    logger.debug(f"Read first byte: {chunk.hex()}")
                else:
                    time.sleep(0.01)
            
            if len(response) == 0:
                logger.warning("No response received")
                return b''
            
            # Now read any additional bytes that might be available
            # Give the device time to send the full response
            time.sleep(0.02)
            
            additional_attempts = 5
            for _ in range(additional_attempts):
                if self.serial_conn.in_waiting > 0:
                    chunk = self.serial_conn.read(self.serial_conn.in_waiting)
                    response.extend(chunk)
                    logger.debug(f"Read additional chunk: {chunk.hex()}")
                    time.sleep(0.01)  # Small delay between reads
                else:
                    break
            
            logger.debug(f"Final response ({len(response)} bytes): {response.hex()}")
            
            # Handle single-byte responses (might be error codes)
            if len(response) == 1:
                response_byte = response[0]
                if response_byte == 0x00:
                    logger.info("Received single-byte response: 0x00 (possible success/no-cart)")
                elif response_byte == 0xFF:
                    logger.warning("Received single-byte response: 0xFF (possible error)")
                else:
                    logger.info(f"Received single-byte response: 0x{response_byte:02X}")
            
            return bytes(response)
            
        except Exception as e:
            logger.error(f"Command send/receive failed: {e}")
            raise
    
    def flush_buffers(self):
        """Flush input and output buffers"""
        if self.is_connected():
            self.serial_conn.reset_input_buffer()
            self.serial_conn.reset_output_buffer()
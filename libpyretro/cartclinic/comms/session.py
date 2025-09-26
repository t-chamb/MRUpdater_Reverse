# Source Generated with Decompyle++
# File: session.pyc (Python 3.10)

import logging
import serial
import time
from typing import Optional, Any

logger = logging.getLogger('mrupdater')

class Session:
    """Communication session with Chromatic device"""
    
    def __init__(self, port=None, baudrate=115200):
        self.port = port
        self.baudrate = baudrate
        self._serial = None
        self._connected = False
    
    def connect(self):
        """Connect to device"""
        try:
            self._serial = serial.Serial(self.port, self.baudrate, timeout=1.0)
            self._connected = True
            logger.info(f"Connected to {self.port}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from device"""
        if self._serial:
            self._serial.close()
            self._serial = None
        self._connected = False
    
    def send_command(self, command: bytes) -> Optional[bytes]:
        """Send command and receive response"""
        if not self._connected or not self._serial:
            return None
        
        try:
            self._serial.write(command)
            response = self._serial.read(1024)  # Read up to 1KB
            return response
        except Exception as e:
            logger.error(f"Communication error: {e}")
            return None
    
    def is_connected(self) -> bool:
        """Check if session is connected"""
        return self._connected and self._serial and self._serial.is_open

class Transport:
    """Transport layer for communication"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def send(self, data: bytes) -> bool:
        """Send data through transport"""
        response = self.session.send_command(data)
        return response is not None

class Transporter:
    """High-level transporter interface"""
    
    def __init__(self, transport: Transport):
        self.transport = transport
        self._running = False
    
    def start(self):
        """Start transporter"""
        self._running = True
    
    def stop(self):
        """Stop transporter"""
        self._running = False

class TransportKind:
    """Transport kind enumeration"""
    USB_SERIAL = "usb_serial"
    TCP = "tcp"

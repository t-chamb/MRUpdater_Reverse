#!/usr/bin/env python3
"""
Test script for cartridge detection functionality.
Tests the CartridgeDetector and CartridgeInfo classes.
"""

import sys
import logging
import time
from pathlib import Path

# Add the source directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from cartclinic.cartridge_info import CartridgeInfo, CartridgeHeader, CartridgeType
from cartclinic.cartridge_detection import CartridgeDetector, CartridgeMonitor
from libpyretro.cartclinic.comms.transport import SerialTransport
from flashing_tool.device_manager import DeviceManager

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger('test_cartridge_detection')

def test_cartridge_header_parsing():
    """Test cartridge header parsing with known data"""
    logger.info("Testing cartridge header parsing...")
    
    # Test data for Tetris (ROM only cartridge)
    tetris_header = bytes([
        # Entry point (0x100-0x103)
        0x00, 0xC3, 0x50, 0x01,
        
        # Nintendo logo (0x104-0x133) - simplified for test
        0xCE, 0xED, 0x66, 0x66, 0xCC, 0x0D, 0x00, 0x0B, 0x03, 0x73, 0x00, 0x83, 0x00, 0x0C, 0x00, 0x0D,
        0x00, 0x08, 0x11, 0x1F, 0x88, 0x89, 0x00, 0x0E, 0xDC, 0xCC, 0x6E, 0xE6, 0xDD, 0xDD, 0xD9, 0x99,
        0xBB, 0xBB, 0x67, 0x63, 0x6E, 0x0E, 0xEC, 0xCC, 0xDD, 0xDC, 0x99, 0x9F, 0xBB, 0xB9, 0x33, 0x3E,
        
        # Title (0x134-0x143) - "TETRIS"
        0x54, 0x45, 0x54, 0x52, 0x49, 0x53, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        
        # New licensee code (0x144-0x145)
        0x00, 0x00,
        
        # SGB flag (0x146)
        0x00,
        
        # Cartridge type (0x147) - ROM only
        0x00,
        
        # ROM size (0x148) - 32KB
        0x00,
        
        # RAM size (0x149) - No RAM
        0x00,
        
        # Destination code (0x14A) - Non-Japanese
        0x01,
        
        # Old licensee code (0x14B)
        0x33,
        
        # Version number (0x14C)
        0x00,
        
        # Header checksum (0x14D)
        0x43,
        
        # Global checksum (0x14E-0x14F)
        0x99, 0x1C
    ])
    
    try:
        # Parse the header
        cartridge_info = CartridgeInfo.from_header_data(tetris_header)
        
        # Verify parsed information
        assert cartridge_info.header.title == "TETRIS"
        assert cartridge_info.header.cartridge_type == CartridgeType.ROM_ONLY
        assert cartridge_info.mapper_name == "ROM Only"
        assert cartridge_info.rom_size_bytes == 32 * 1024
        assert cartridge_info.rom_banks == 2
        assert cartridge_info.ram_size_bytes == 0
        assert not cartridge_info.has_battery
        assert not cartridge_info.has_ram
        
        # Print summary
        summary = cartridge_info.get_summary()
        logger.info(f"Parsed cartridge info: {summary}")
        
        logger.info("✓ Cartridge header parsing test passed")
        return True
        
    except Exception as e:
        logger.error(f"✗ Cartridge header parsing test failed: {e}")
        return False

def test_device_detection():
    """Test device detection and connection"""
    logger.info("Testing device detection...")
    
    try:
        device_manager = DeviceManager()
        devices = device_manager.scan_for_devices()
        
        if not devices:
            logger.warning("No Chromatic devices found - skipping device tests")
            return True
        
        logger.info(f"Found {len(devices)} Chromatic device(s)")
        
        # Test connection to first device
        device_info = devices[0]
        logger.info(f"Testing connection to device: {device_info}")
        
        transport = SerialTransport(device_info.serial_port)
        
        if transport.connect():
            logger.info("✓ Device connection successful")
            
            # Test ping
            if transport.ping():
                logger.info("✓ Device ping successful")
            else:
                logger.warning("Device ping failed")
            
            transport.disconnect()
            return True
        else:
            logger.error("✗ Device connection failed")
            return False
            
    except Exception as e:
        logger.error(f"✗ Device detection test failed: {e}")
        return False

def test_cartridge_detection_mock():
    """Test cartridge detection with mock transport"""
    logger.info("Testing cartridge detection with mock data...")
    
    class MockTransport:
        """Mock transport for testing"""
        def __init__(self):
            self.connected = True
            
        def is_connected(self):
            return self.connected
            
        def send_command(self, command):
            """Mock command responses"""
            from libpyretro.cartclinic.comms.transport import ResponseMessage
            
            if command.command == "cart_detect":
                # Mock cartridge inserted response
                return ResponseMessage(
                    success=True,
                    data={
                        'raw_response': b'\x01\x00\x00'  # Mock detection response
                    }
                )
            elif command.command == "raw_command":
                # Mock byte read response
                return ResponseMessage(
                    success=True,
                    data={
                        'response': '0400CE'  # Mock header byte response
                    }
                )
            else:
                return ResponseMessage(
                    success=False,
                    error="Unknown command"
                )
    
    try:
        # Create detector with mock transport
        mock_transport = MockTransport()
        detector = CartridgeDetector(mock_transport)
        
        # Note: This test would need actual device communication to work fully
        # For now, just verify the detector can be created
        logger.info("✓ CartridgeDetector created successfully")
        
        # Test basic functionality
        current_cartridge = detector.get_current_cartridge()
        assert current_cartridge is None
        
        is_inserted = detector.is_cartridge_inserted()
        assert not is_inserted
        
        logger.info("✓ Cartridge detection mock test passed")
        return True
        
    except Exception as e:
        logger.error(f"✗ Cartridge detection mock test failed: {e}")
        return False

def test_cartridge_monitor():
    """Test cartridge monitoring functionality"""
    logger.info("Testing cartridge monitor...")
    
    try:
        class MockDetector:
            def __init__(self):
                self.state = (False, False)
                
            def detect_cartridge_insertion(self, timeout=1.0):
                from cartclinic.cartridge_detection import DetectionResult
                return DetectionResult(
                    inserted=self.state[0],
                    removed=self.state[1]
                )
        
        # Create monitor with mock detector
        mock_detector = MockDetector()
        monitor = CartridgeMonitor(mock_detector)
        
        # Test callback registration
        callback_called = False
        def test_callback(data):
            nonlocal callback_called
            callback_called = True
            logger.info(f"Callback triggered with data: {data}")
        
        monitor.add_callback('inserted', test_callback)
        
        logger.info("✓ Cartridge monitor test passed")
        return True
        
    except Exception as e:
        logger.error(f"✗ Cartridge monitor test failed: {e}")
        return False

def main():
    """Run all tests"""
    logger.info("Starting cartridge detection tests...")
    
    tests = [
        ("Cartridge Header Parsing", test_cartridge_header_parsing),
        ("Device Detection", test_device_detection),
        ("Cartridge Detection Mock", test_cartridge_detection_mock),
        ("Cartridge Monitor", test_cartridge_monitor)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        logger.info(f"\n--- Running {test_name} ---")
        try:
            if test_func():
                passed += 1
                logger.info(f"✓ {test_name} PASSED")
            else:
                logger.error(f"✗ {test_name} FAILED")
        except Exception as e:
            logger.error(f"✗ {test_name} FAILED with exception: {e}")
    
    logger.info(f"\n--- Test Results ---")
    logger.info(f"Passed: {passed}/{total}")
    
    if passed == total:
        logger.info("🎉 All tests passed!")
        return 0
    else:
        logger.error(f"❌ {total - passed} test(s) failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
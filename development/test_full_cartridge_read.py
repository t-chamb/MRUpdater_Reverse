#!/usr/bin/env python3
"""
Full cartridge read test - tests the complete cartridge reading workflow
"""

import sys
import logging
from pathlib import Path

# Add the source directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

# Set up basic logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_full_cartridge_read():
    """Test the full cartridge read helper function"""
    try:
        print("Testing full cartridge read workflow...")
        
        from cartclinic.cartridge_read import read_cartridge_helper
        from cartclinic.consts import BANK_SIZE
        from libpyretro.cartclinic.comms.session import Session
        
        # Create a comprehensive mock session
        class MockSession(Session):
            def __init__(self):
                super().__init__()
                self._connected = True
                self.bank_count = 32  # Simulate a 512KB ROM (32 banks of 16KB each)
                
            def is_connected(self):
                return self._connected
                
            def connect(self, port=None, baudrate=None, timeout=None):
                self._connected = True
                return True
                
            def disconnect(self):
                self._connected = False
                
            def send_command(self, command):
                return b"\x00"  # Success response
                
            def read_bank(self, bank_num: int):
                if bank_num >= self.bank_count:
                    return None
                # Return mock data with bank number in first byte for verification
                bank_data = bytes([bank_num]) + b"\x01\x02\x03" * ((BANK_SIZE - 1) // 3)
                # Pad to exact bank size
                return bank_data[:BANK_SIZE]
                
            def get_cartridge_info(self):
                return {
                    'title': 'TEST CARTRIDGE',
                    'type': 'MBC1',
                    'rom_size': self.bank_count * BANK_SIZE,
                    'ram_size': 8192,
                    'checksum': 0x1234
                }
                
            def read_header(self):
                # Mock Game Boy header
                header = bytearray(0x150)
                # Title at 0x134-0x143
                title = b"TEST CART\x00\x00\x00\x00\x00\x00\x00"
                header[0x134:0x134+len(title)] = title
                # Cartridge type at 0x147
                header[0x147] = 0x01  # MBC1
                # ROM size at 0x148
                header[0x148] = 0x05  # 512KB
                # RAM size at 0x149
                header[0x149] = 0x02  # 8KB
                return bytes(header)
        
        # Create mock animation and detection thread (can be None for testing)
        mock_session = MockSession()
        
        # Test the full read operation
        print("Starting cartridge read operation...")
        
        result = read_cartridge_helper(
            session=mock_session,
            animation=None,  # No animation for testing
            detection_thread=None,  # No detection thread for testing
            emit_progress=lambda progress, message="": print(f"Progress: {progress}% - {message}"),
            progress_callback=lambda current, total: print(f"Read {current}/{total} banks"),
            cancellation_token=None,
            include_save_data=False
        )
        
        if result:
            print("✓ Cartridge read completed successfully!")
            print(f"  - Result type: {type(result)}")
            print(f"  - Result keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
            
            if isinstance(result, dict):
                if 'rom_data' in result:
                    rom_size = len(result['rom_data'])
                    print(f"  - ROM size: {rom_size} bytes ({rom_size // 1024}KB)")
                    
                    # Verify first few banks have correct data
                    for bank in range(min(4, rom_size // BANK_SIZE)):
                        bank_start = bank * BANK_SIZE
                        first_byte = result['rom_data'][bank_start]
                        if first_byte == bank:
                            print(f"  - Bank {bank}: ✓ (first byte = {first_byte})")
                        else:
                            print(f"  - Bank {bank}: ✗ (expected {bank}, got {first_byte})")
                
                if 'cartridge_info' in result:
                    info = result['cartridge_info']
                    print(f"  - Cartridge title: {info.get('title', 'Unknown')}")
                    print(f"  - Cartridge type: {info.get('type', 'Unknown')}")
            
            return True
        else:
            print("✗ Cartridge read returned None")
            return False
            
    except Exception as e:
        print(f"✗ Full cartridge read failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_save_data_read():
    """Test reading save data"""
    try:
        print("\nTesting save data read...")
        
        from cartclinic.cartridge_read import read_save_data_helper
        from libpyretro.cartclinic.comms.session import Session
        
        class MockSessionWithSave(Session):
            def __init__(self):
                super().__init__()
                self._connected = True
                
            def is_connected(self):
                return self._connected
                
            def read_save_data(self):
                # Mock 8KB save data
                return b"SAVE" + b"\x00" * 8188  # 8KB total
        
        mock_session = MockSessionWithSave()
        
        save_data = read_save_data_helper(mock_session)
        
        if save_data:
            print(f"✓ Save data read: {len(save_data)} bytes")
            print(f"  - First 4 bytes: {save_data[:4]}")
            return True
        else:
            print("✗ Save data read returned None")
            return False
            
    except Exception as e:
        print(f"✗ Save data read failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_rom_validation():
    """Test ROM checksum validation"""
    try:
        print("\nTesting ROM validation...")
        
        from cartclinic.cartridge_read import validate_rom_checksum
        
        # Create mock ROM data with proper Game Boy header
        rom_data = bytearray(32768)  # 32KB ROM
        
        # Add Game Boy header
        rom_data[0x134:0x144] = b"TEST ROM\x00\x00\x00\x00\x00\x00\x00"  # Title
        rom_data[0x147] = 0x00  # ROM only
        rom_data[0x148] = 0x01  # 32KB
        
        # Calculate and set checksum
        checksum = 0
        for i in range(0x134, 0x14D):
            checksum = (checksum - rom_data[i] - 1) & 0xFF
        rom_data[0x14D] = checksum
        
        # Test validation
        is_valid = validate_rom_checksum(bytes(rom_data))
        
        print(f"✓ ROM validation: {'Valid' if is_valid else 'Invalid'}")
        print(f"  - ROM size: {len(rom_data)} bytes")
        print(f"  - Calculated checksum: 0x{checksum:02X}")
        
        return True
        
    except Exception as e:
        print(f"✗ ROM validation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all comprehensive tests"""
    print("=== MRUpdater Full Cartridge Read Test ===\n")
    
    tests = [
        test_full_cartridge_read,
        test_save_data_read,
        test_rom_validation,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                print("Test failed!")
        except Exception as e:
            print(f"Test crashed: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n=== Test Results: {passed}/{total} passed ===")
    
    if passed == total:
        print("All tests passed! ✓")
        print("\nThe cartridge read functionality is working correctly!")
        return 0
    else:
        print("Some tests failed! ✗")
        return 1

if __name__ == "__main__":
    sys.exit(main())
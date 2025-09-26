#!/usr/bin/env python3
"""
Standalone test for cartridge read functionality
This bypasses the GUI and complex dependencies to test just the core cartridge reading
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

def test_cartridge_read_imports():
    """Test that we can import the cartridge read modules"""
    try:
        print("Testing cartridge read imports...")
        
        # Test basic imports
        from cartclinic.cartridge_read import read_cartridge_helper, read_single_flash_bank
        print("✓ Cartridge read functions imported successfully")
        
        from cartclinic.consts import BANK_SIZE
        print("✓ Constants imported successfully")
        
        from libpyretro.cartclinic.comms.session import Session
        print("✓ Session imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False

def test_session_creation():
    """Test creating a Session instance"""
    try:
        print("\nTesting Session creation...")
        
        from libpyretro.cartclinic.comms.session import Session
        
        # Create a mock session for testing
        class MockSession(Session):
            def __init__(self):
                self.is_connected = False
                
            def connect(self):
                self.is_connected = True
                return True
                
            def disconnect(self):
                self.is_connected = False
                
            def send_command(self, command, data=None):
                return b"mock_response"
                
            def read_response(self, expected_length=None):
                return b"mock_data"
        
        mock_session = MockSession()
        
        print("✓ Session created successfully")
        print(f"  - Session type: {type(mock_session).__name__}")
        
        return True
        
    except Exception as e:
        print(f"✗ Session creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_cartridge_read_function():
    """Test cartridge read helper function"""
    try:
        print("\nTesting cartridge read function...")
        
        from cartclinic.cartridge_read import read_single_flash_bank
        from cartclinic.consts import BANK_SIZE
        
        # Create mock session
        class MockSession:
            def __init__(self):
                self.is_connected = True
                
            def send_command(self, command, data=None):
                return b"OK"
                
            def read_response(self, expected_length=None):
                # Mock bank data
                return b"\x00\x01\x02\x03" * (BANK_SIZE // 4)
                
            def read_bank(self, bank_num: int):
                # Mock reading a bank - return BANK_SIZE bytes
                return b"\x00\x01\x02\x03" * (BANK_SIZE // 4)
        
        mock_session = MockSession()
        
        # Test reading a single bank
        bank_data = read_single_flash_bank(mock_session, bank=0)
        
        if bank_data:
            print(f"✓ Bank read completed: {len(bank_data)} bytes")
            print(f"  - Expected size: {BANK_SIZE} bytes")
            print(f"  - Match: {'✓' if len(bank_data) == BANK_SIZE else '✗'}")
        else:
            print("✗ Bank read returned None")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Cartridge read function failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("=== MRUpdater Cartridge Read Standalone Test ===\n")
    
    tests = [
        test_cartridge_read_imports,
        test_session_creation,
        test_cartridge_read_function,
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
        return 0
    else:
        print("Some tests failed! ✗")
        return 1

if __name__ == "__main__":
    sys.exit(main())
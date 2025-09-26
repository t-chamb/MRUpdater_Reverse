#!/usr/bin/env python3
"""
Test the protocol fix for cartridge detection
"""

import sys
import logging
import time
from pathlib import Path

# Add the source directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

def setup_logging():
    """Set up debug logging"""
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def test_cartridge_detection():
    """Test cartridge detection with improved protocol handling"""
    print("=== Testing Cartridge Detection Protocol Fix ===")
    
    try:
        from flashing_tool.chromatic import Chromatic
        from libpyretro.cartclinic.comms.session import Session
        
        print("1. Connecting to Chromatic device...")
        chromatic = Chromatic()
        
        # Wait for device to be ready
        max_wait = 15
        wait_time = 0
        
        while chromatic.current_state.id != 'ready_to_flash' and wait_time < max_wait:
            chromatic.update_status()
            print(f"   Device state: {chromatic.current_state.id}")
            time.sleep(1)
            wait_time += 1
            
        if chromatic.current_state.id != 'ready_to_flash':
            print(f"✗ Device not ready. Current state: {chromatic.current_state.id}")
            return False
            
        print("✓ Chromatic device ready!")
        
        # Get MCU port
        mcu_port = chromatic.mcu_port
        if not mcu_port:
            print("✗ No MCU port found")
            return False
            
        print(f"✓ MCU port: {mcu_port}")
        
        print("2. Testing cartridge detection...")
        session = Session()
        
        if not session.connect(port=mcu_port, baudrate=115200, timeout=5):
            print("✗ Failed to connect to device")
            return False
            
        print("✓ Connected to device")
        
        try:
            # Test cartridge detection
            cartridge_info = session.get_cartridge_info()
            
            if cartridge_info:
                print("✓ Cartridge detected successfully!")
                print(f"   Title: {cartridge_info.get('title', 'Unknown')}")
                print(f"   Mapper: {cartridge_info.get('mapper', 'Unknown')}")
                print(f"   ROM Size: {cartridge_info.get('rom_size', 0)} bytes")
                print(f"   RAM Size: {cartridge_info.get('ram_size', 0)} bytes")
                print(f"   Has Battery: {cartridge_info.get('has_battery', False)}")
                return True
            else:
                print("! No cartridge detected (insert a Game Boy cartridge)")
                return True  # This is not an error if no cart is inserted
                
        finally:
            session.disconnect()
            print("3. Disconnected from device")
            
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    setup_logging()
    
    print("Protocol Fix Test")
    print("=" * 30)
    print("This test verifies the cartridge detection protocol fix.")
    print("Make sure a Game Boy cartridge is inserted for full testing.")
    print()
    
    success = test_cartridge_detection()
    
    if success:
        print("\n✓ Protocol test completed successfully!")
        print("\nNext steps:")
        print("1. Try running the full cartridge read demo")
        print("2. Test with different cartridge types")
    else:
        print("\n✗ Protocol test failed")
        print("Check the debug logs for more information")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
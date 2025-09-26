#!/usr/bin/env python3
"""
Debug cartridge detection issues
Tests the basic communication protocol step by step
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

def test_device_connection():
    """Test basic device connection"""
    print("=== Testing Device Connection ===")
    
    try:
        from flashing_tool.chromatic import Chromatic
        
        print("1. Initializing Chromatic device...")
        chromatic = Chromatic()
        
        # Wait for device to be ready
        max_wait = 15  # seconds
        wait_time = 0
        print("2. Waiting for device to be ready...")
        
        while chromatic.current_state.id != 'ready_to_flash' and wait_time < max_wait:
            chromatic.update_status()
            print(f"   Device state: {chromatic.current_state.id}")
            time.sleep(1)
            wait_time += 1
            
        if chromatic.current_state.id != 'ready_to_flash':
            print(f"✗ Device not ready after {max_wait}s. Current state: {chromatic.current_state.id}")
            return False
            
        print("✓ Chromatic device ready!")
        
        # Get the MCU port
        mcu_port = chromatic.mcu_port
        if not mcu_port:
            print("✗ No MCU port found")
            return False
            
        print(f"✓ MCU port found: {mcu_port}")
        return True, mcu_port
        
    except Exception as e:
        print(f"✗ Device connection failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_raw_serial_connection(mcu_port):
    """Test raw serial connection"""
    print("\n=== Testing Raw Serial Connection ===")
    
    try:
        import serial
        
        print(f"1. Opening serial port {mcu_port}...")
        ser = serial.Serial(mcu_port, 115200, timeout=2)
        
        if ser.is_open:
            print("✓ Serial port opened successfully")
        else:
            print("✗ Failed to open serial port")
            return False
            
        # Test basic communication
        print("2. Testing basic communication...")
        
        # Send a simple command and see what we get back
        test_data = b'\x00\x01\x02\x03'
        ser.write(test_data)
        time.sleep(0.1)
        
        response = ser.read(100)  # Read up to 100 bytes
        print(f"   Sent: {test_data.hex()}")
        print(f"   Received: {response.hex() if response else 'No response'}")
        
        ser.close()
        print("✓ Serial test completed")
        return True
        
    except Exception as e:
        print(f"✗ Serial connection failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_cart_detection_protocol(mcu_port):
    """Test cartridge detection protocol step by step"""
    print("\n=== Testing Cart Detection Protocol ===")
    
    try:
        from libpyretro.cartclinic.comms.session import Session
        from libpyretro.cartclinic.cart_api import CartAPI_Builder, CartAPI_Parser
        
        print("1. Creating session...")
        session = Session()
        
        print("2. Connecting to device...")
        if not session.connect(port=mcu_port, baudrate=115200, timeout=5):
            print("✗ Failed to connect to device")
            return False
            
        print("✓ Connected to device")
        
        print("3. Testing cartridge detection command...")
        
        # Build detection command
        detect_cmd = CartAPI_Builder.detect_cart()
        print(f"   Detection command: {detect_cmd.hex()}")
        
        # Send command and get response
        try:
            response = session.send_command(detect_cmd)
            print(f"   Raw response: {response.hex() if response else 'No response'}")
            
            if response:
                # Try to parse the response
                try:
                    inserted, removed = CartAPI_Parser.cart_detection_status(response)
                    print(f"   Parsed result: inserted={inserted}, removed={removed}")
                    
                    if inserted:
                        print("✓ Cartridge detected!")
                    else:
                        print("! No cartridge detected (this is normal if no cart is inserted)")
                        
                except Exception as parse_error:
                    print(f"   Parse error: {parse_error}")
                    print("   This might indicate a protocol mismatch")
                    
        except Exception as cmd_error:
            print(f"   Command error: {cmd_error}")
            
        finally:
            session.disconnect()
            print("4. Disconnected from device")
            
        return True
        
    except Exception as e:
        print(f"✗ Protocol test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_protocol_commands():
    """Test individual protocol commands"""
    print("\n=== Testing Protocol Commands ===")
    
    try:
        from libpyretro.cartclinic.cart_api import CartAPI_Builder
        
        print("1. Testing command builders...")
        
        # Test detection command
        detect_cmd = CartAPI_Builder.detect_cart()
        print(f"   Detect cart: {detect_cmd.hex()}")
        
        # Test read byte command
        read_cmd = CartAPI_Builder.read_byte(0, 0, 0)
        print(f"   Read byte (0,0,0): {read_cmd.hex()}")
        
        # Test bank setting
        bank_cmds = CartAPI_Builder.set_bank(1)
        print(f"   Set bank 1: {[cmd.hex() for cmd in bank_cmds]}")
        
        print("✓ Command builders working")
        return True
        
    except Exception as e:
        print(f"✗ Protocol command test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    setup_logging()
    
    print("MRUpdater Cartridge Detection Debug Tool")
    print("=" * 50)
    
    # Test 1: Device connection
    result = test_device_connection()
    if not result:
        print("\n✗ Device connection test failed")
        return 1
        
    success, mcu_port = result
    if not success:
        return 1
    
    # Test 2: Raw serial connection
    if not test_raw_serial_connection(mcu_port):
        print("\n✗ Raw serial test failed")
        return 1
    
    # Test 3: Protocol commands
    if not test_protocol_commands():
        print("\n✗ Protocol command test failed")
        return 1
    
    # Test 4: Cart detection protocol
    if not test_cart_detection_protocol(mcu_port):
        print("\n✗ Cart detection protocol test failed")
        return 1
    
    print("\n" + "=" * 50)
    print("✓ All tests completed!")
    print("\nNext steps:")
    print("1. Insert a Game Boy cartridge if not already inserted")
    print("2. Run the full cartridge read test")
    print("3. Check the logs for any protocol mismatches")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
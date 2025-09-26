#!/usr/bin/env python3
"""
Test cartridge detection with MRTetris cartridge inserted
Try different protocol approaches to properly detect the cartridge
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

def test_different_detection_approaches():
    """Test different approaches to detect the MRTetris cartridge"""
    print("=== Testing MRTetris Cartridge Detection ===")
    print("Cartridge: MRTetris (confirmed inserted)")
    print()
    
    try:
        from flashing_tool.chromatic import Chromatic
        from libpyretro.cartclinic.comms.session import Session
        from libpyretro.cartclinic.cart_api import CartAPI_Builder, CartAPI_Parser
        
        print("1. Connecting to Chromatic device...")
        chromatic = Chromatic()
        
        # Wait for device to be ready
        max_wait = 10
        wait_time = 0
        
        while chromatic.current_state.id != 'ready_to_flash' and wait_time < max_wait:
            chromatic.update_status()
            time.sleep(1)
            wait_time += 1
            
        if chromatic.current_state.id != 'ready_to_flash':
            print(f"✗ Device not ready. Current state: {chromatic.current_state.id}")
            return False
            
        print("✓ Device ready!")
        
        mcu_port = chromatic.mcu_port
        print(f"✓ MCU port: {mcu_port}")
        
        print("\n2. Testing different detection approaches...")
        session = Session()
        
        if not session.connect(port=mcu_port, baudrate=115200, timeout=5):
            print("✗ Failed to connect")
            return False
            
        print("✓ Connected")
        
        try:
            # Approach 1: Standard detect command
            print("\nApproach 1: Standard detect command")
            detect_cmd = CartAPI_Builder.detect_cart()
            print(f"   Command: {detect_cmd.hex()}")
            
            response = session.send_command(detect_cmd)
            print(f"   Response: {response.hex() if response else 'None'}")
            
            if response and len(response) >= 4:
                try:
                    inserted, removed = CartAPI_Parser.cart_detection_status(response)
                    print(f"   Parsed: inserted={inserted}, removed={removed}")
                except Exception as e:
                    print(f"   Parse error: {e}")
            
            # Approach 2: Try reading from cartridge header directly
            print("\nApproach 2: Direct header read (address 0x0100)")
            read_cmd = CartAPI_Builder.read_byte(1, 0, 0)  # Block 1, offset 0, bank 0 = address 0x0100
            print(f"   Command: {read_cmd.hex()}")
            
            response = session.send_command(read_cmd)
            print(f"   Response: {response.hex() if response else 'None'}")
            
            if response and len(response) >= 3:
                try:
                    addr, data = CartAPI_Parser.byte_read(response)
                    print(f"   Read from 0x{addr:04X}: 0x{data:02X}")
                    if data != 0x00:
                        print("   ✓ Non-zero data suggests cartridge is present!")
                except Exception as e:
                    print(f"   Parse error: {e}")
            
            # Approach 3: Try reading Game Boy header signature
            print("\nApproach 3: Read Game Boy header signature (0x0104-0x0133)")
            header_bytes = []
            
            for addr in range(0x0104, 0x0108):  # Just read first few bytes of Nintendo logo
                block = addr // 256
                offset = addr % 256
                bank_index = 0
                
                read_cmd = CartAPI_Builder.read_byte(block, offset, bank_index)
                response = session.send_command(read_cmd)
                
                if response and len(response) >= 3:
                    try:
                        read_addr, data = CartAPI_Parser.byte_read(response)
                        header_bytes.append(data)
                        print(f"   0x{addr:04X}: 0x{data:02X}")
                    except Exception as e:
                        print(f"   Error reading 0x{addr:04X}: {e}")
                        break
                else:
                    print(f"   No response for 0x{addr:04X}")
                    break
                    
                time.sleep(0.01)  # Small delay between reads
            
            if header_bytes:
                print(f"   Header bytes: {' '.join(f'{b:02X}' for b in header_bytes)}")
                # Nintendo logo starts with CE ED 66 66 CC 0D 00 0B
                expected_start = [0xCE, 0xED, 0x66, 0x66]
                if len(header_bytes) >= 4 and header_bytes[:4] == expected_start:
                    print("   ✓ Nintendo logo detected! Cartridge is definitely present!")
                elif any(b != 0x00 for b in header_bytes):
                    print("   ✓ Non-zero header data suggests cartridge is present!")
                else:
                    print("   ? All zeros - might indicate no cartridge or read issue")
            
            # Approach 4: Try reading cartridge title area
            print("\nApproach 4: Read cartridge title area (0x0134-0x0143)")
            title_bytes = []
            
            for addr in range(0x0134, 0x0140):  # Read first part of title
                block = addr // 256
                offset = addr % 256
                bank_index = 0
                
                read_cmd = CartAPI_Builder.read_byte(block, offset, bank_index)
                response = session.send_command(read_cmd)
                
                if response and len(response) >= 3:
                    try:
                        read_addr, data = CartAPI_Parser.byte_read(response)
                        title_bytes.append(data)
                    except Exception as e:
                        print(f"   Error reading title byte: {e}")
                        break
                else:
                    break
                    
                time.sleep(0.01)
            
            if title_bytes:
                # Convert to string, handling null bytes
                title_str = ''.join(chr(b) if 32 <= b <= 126 else '.' for b in title_bytes)
                print(f"   Title bytes: {' '.join(f'{b:02X}' for b in title_bytes)}")
                print(f"   Title string: '{title_str}'")
                
                if any(b != 0x00 for b in title_bytes):
                    print("   ✓ Title data suggests cartridge is present!")
            
        finally:
            session.disconnect()
            print("\n3. Disconnected")
            
        return True
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    setup_logging()
    
    print("MRTetris Cartridge Detection Test")
    print("=" * 40)
    print("This test assumes MRTetris cartridge is inserted")
    print("and tries different approaches to detect it properly.")
    print()
    
    success = test_different_detection_approaches()
    
    if success:
        print("\n" + "=" * 40)
        print("✓ Test completed!")
        print("\nIf any approach detected the cartridge, we can")
        print("use that method for reliable cartridge reading.")
    else:
        print("\n✗ Test failed")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
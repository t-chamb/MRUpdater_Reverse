#!/usr/bin/env python3
"""
Raw protocol testing - bypass the high-level API and test direct communication
"""

import sys
import logging
import time
import struct
from pathlib import Path

# Add the source directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

def setup_logging():
    """Set up debug logging"""
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def test_raw_protocol():
    """Test raw protocol communication"""
    print("=== Raw Protocol Testing ===")
    
    try:
        from flashing_tool.chromatic import Chromatic
        from libpyretro.cartclinic.comms.transport import SerialTransport
        
        print("1. Connecting to device...")
        chromatic = Chromatic()
        
        # Wait for ready state
        max_wait = 10
        wait_time = 0
        while chromatic.current_state.id != 'ready_to_flash' and wait_time < max_wait:
            chromatic.update_status()
            time.sleep(1)
            wait_time += 1
            
        if chromatic.current_state.id != 'ready_to_flash':
            print(f"✗ Device not ready: {chromatic.current_state.id}")
            return False
            
        mcu_port = chromatic.mcu_port
        print(f"✓ Device ready, port: {mcu_port}")
        
        print("\n2. Testing raw serial communication...")
        transport = SerialTransport(mcu_port, 115200, 2.0)
        
        if not transport.connect():
            print("✗ Failed to connect")
            return False
            
        print("✓ Connected")
        
        # Test different command formats and approaches
        test_commands = [
            # Original detect command
            ("Detect Cart (original)", b'\x05\x00\x00\x00'),
            
            # Try with different framing
            ("Detect Cart (no padding)", b'\x05'),
            ("Detect Cart (3-byte)", b'\x05\x00\x00'),
            ("Detect Cart (5-byte)", b'\x05\x00\x00\x00\x00'),
            
            # Try loopback command (should echo back)
            ("Loopback test", b'\x01\xAA\xBB\xCC'),
            
            # Try read commands with different formats
            ("Read byte (0x0000)", b'\x02\x00\x00\x00'),
            ("Read byte (0x0100)", b'\x02\x00\x01\x00'),
            ("Read byte (alt format)", b'\x02\x01\x00'),
            
            # Try some initialization sequences
            ("Init sequence 1", b'\x00\x00\x00\x00'),
            ("Init sequence 2", b'\xFF\xFF\xFF\xFF'),
            ("Sync pattern", b'\xAA\x55\xAA\x55'),
        ]
        
        print("\n3. Testing different command formats...")
        
        for name, command in test_commands:
            print(f"\n--- {name} ---")
            print(f"Command: {command.hex().upper()}")
            
            try:
                # Clear buffers
                transport.flush_buffers()
                time.sleep(0.01)
                
                # Send command
                response = transport.send_command(command)
                print(f"Response: {response.hex().upper() if response else 'None'}")
                
                if response:
                    print(f"Length: {len(response)} bytes")
                    if len(response) > 0:
                        print(f"First byte: 0x{response[0]:02X}")
                        
                    # Try to interpret as different formats
                    if len(response) >= 4:
                        try:
                            # Try as 4-byte response
                            cmd_id, b1, b2, b3 = struct.unpack('<BBBB', response[:4])
                            print(f"As 4-byte: cmd_id={cmd_id}, data=[{b1:02X}, {b2:02X}, {b3:02X}]")
                        except:
                            pass
                            
                    if len(response) >= 3:
                        try:
                            # Try as 3-byte response
                            cmd_id, addr, data = struct.unpack('<BHB', response[:4] if len(response) >= 4 else response + b'\x00')
                            print(f"As addr/data: cmd_id={cmd_id}, addr=0x{addr:04X}, data=0x{data:02X}")
                        except:
                            pass
                
                # Small delay between commands
                time.sleep(0.1)
                
            except Exception as e:
                print(f"Error: {e}")
        
        print("\n4. Testing continuous read...")
        # Try reading multiple bytes in sequence
        try:
            for addr in range(0x0100, 0x0110):
                # Format: cmd_id (2), addr_low, addr_high, padding
                cmd = struct.pack('<BBBB', 2, addr & 0xFF, (addr >> 8) & 0xFF, 0)
                print(f"Reading 0x{addr:04X}: {cmd.hex()}", end=" -> ")
                
                response = transport.send_command(cmd)
                if response:
                    print(f"{response.hex()}")
                    if len(response) >= 4 and response[0] == 2:
                        # Valid read response
                        _, resp_addr, data_byte = struct.unpack('<BHB', response[:4])
                        print(f"  Success: addr=0x{resp_addr:04X}, data=0x{data_byte:02X}")
                        if data_byte != 0x00:
                            print(f"  *** NON-ZERO DATA FOUND! ***")
                            break
                else:
                    print("No response")
                    
                time.sleep(0.01)
                
        except Exception as e:
            print(f"Continuous read error: {e}")
        
        transport.disconnect()
        print("\n5. Disconnected")
        
        return True
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    setup_logging()
    
    print("Raw Protocol Testing")
    print("=" * 30)
    print("This test bypasses high-level APIs and tests raw communication")
    print()
    
    success = test_raw_protocol()
    
    if success:
        print("\n✓ Raw protocol test completed!")
    else:
        print("\n✗ Raw protocol test failed")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
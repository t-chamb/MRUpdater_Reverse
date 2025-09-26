#!/usr/bin/env python3
"""
Quick ROM Test - Test reading just the first few KB to check speed
"""

import sys
import time
import logging
from pathlib import Path

# Add the source directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

def test_read_speed():
    """Test reading speed for first few KB"""
    
    print("=== Quick ROM Read Speed Test ===")
    
    try:
        from libpyretro.cartclinic.comms.session import Session
        from flashing_tool.chromatic import Chromatic
        from cartclinic.consts import BANK_SIZE
        from libpyretro.cartclinic.cart_api import CartAPI_Builder, CartAPI_Parser
        
        # Connect to device
        print("Connecting to Chromatic...")
        chromatic = Chromatic()
        
        # Wait for ready
        max_wait = 10
        wait_time = 0
        while chromatic.current_state.id != 'ready_to_flash' and wait_time < max_wait:
            chromatic.update_status()
            time.sleep(0.5)
            wait_time += 0.5
            
        if chromatic.current_state.id != 'ready_to_flash':
            print(f"✗ Device not ready: {chromatic.current_state.id}")
            return False
            
        print("✓ Device ready")
        
        # Connect session
        session = Session()
        if not session.connect(port=chromatic.mcu_port, baudrate=115200, timeout=5):
            print("✗ Failed to connect")
            return False
            
        print("✓ Connected")
        
        try:
            # Test reading just first 1KB (64 bytes)
            print("\nTesting read speed for first 64 bytes...")
            
            start_time = time.time()
            data = bytearray()
            
            # Read first 64 bytes from bank 0
            for addr in range(64):
                block = addr // 256
                offset = addr % 256
                bank_index = 0  # Bank 0
                
                read_cmd = CartAPI_Builder.read_byte(block, offset, bank_index)
                response = session.send_command(read_cmd)
                addr_read, data_byte = CartAPI_Parser.byte_read(response)
                
                data.append(data_byte)
                
                if addr % 16 == 15:  # Every 16 bytes
                    elapsed = time.time() - start_time
                    speed = (addr + 1) / elapsed if elapsed > 0 else 0
                    print(f"  Read {addr + 1:2d} bytes in {elapsed:.2f}s ({speed:.1f} bytes/s)")
            
            elapsed = time.time() - start_time
            speed = 64 / elapsed if elapsed > 0 else 0
            
            print(f"\nResults:")
            print(f"  64 bytes read in {elapsed:.2f} seconds")
            print(f"  Speed: {speed:.1f} bytes/second")
            print(f"  Estimated time for 512KB ROM: {512*1024/speed/60:.1f} minutes")
            
            # Show first 32 bytes as hex
            print(f"\nFirst 32 bytes:")
            hex_str = ' '.join(f'{b:02x}' for b in data[:32])
            print(f"  {hex_str}")
            
            # Check if it looks like Game Boy header
            if len(data) >= 32:
                # Check for Nintendo logo area (should have specific pattern)
                nintendo_area = data[4:36]  # 0x104-0x133 area
                if any(b != 0 for b in nintendo_area):
                    print("  ✓ Looks like valid Game Boy ROM data")
                else:
                    print("  ? Data might not be from ROM area")
            
            return True
            
        finally:
            session.disconnect()
            print("Disconnected")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_read_speed()
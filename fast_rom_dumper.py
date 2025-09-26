#!/usr/bin/env python3
"""
Fast ROM Dumper - Optimized for speed by reducing USB delays
"""

import sys
import time
import logging
from pathlib import Path

# Add the source directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

class FastSerialTransport:
    """Optimized serial transport with minimal delays"""
    
    def __init__(self):
        self.serial_conn = None
        self.logger = logging.getLogger(__name__)
    
    def connect(self, port, baudrate=115200, timeout=1):
        """Connect to serial port"""
        try:
            import serial
            self.serial_conn = serial.Serial(
                port=port,
                baudrate=baudrate,
                timeout=timeout,
                write_timeout=timeout
            )
            return True
        except Exception as e:
            self.logger.error(f"Failed to connect: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from serial port"""
        if self.serial_conn:
            self.serial_conn.close()
            self.serial_conn = None
    
    def is_connected(self):
        """Check if connected"""
        return self.serial_conn is not None and self.serial_conn.is_open
    
    def send_command_fast(self, command):
        """Send command with minimal delays"""
        if not self.is_connected():
            raise Exception("Not connected")
        
        try:
            # Send command
            self.serial_conn.write(command)
            
            # Read response with minimal delay
            response = bytearray()
            max_wait_time = 0.5  # Reduced from longer waits
            start_time = time.time()
            
            # Wait for at least 4 bytes (our expected response size)
            while len(response) < 4 and (time.time() - start_time) < max_wait_time:
                if self.serial_conn.in_waiting > 0:
                    chunk = self.serial_conn.read(self.serial_conn.in_waiting)
                    response.extend(chunk)
                else:
                    time.sleep(0.001)  # Much smaller delay - 1ms instead of 10ms
            
            return bytes(response)
            
        except Exception as e:
            self.logger.error(f"Fast command failed: {e}")
            raise

def fast_dump_rom(output_file, max_banks=2):
    """Fast ROM dump with optimized transport"""
    
    print("=== Fast ROM Dumper ===")
    
    try:
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
        
        # Use fast transport
        transport = FastSerialTransport()
        if not transport.connect(chromatic.mcu_port, baudrate=115200, timeout=1):
            print("✗ Failed to connect")
            return False
            
        print("✓ Connected with fast transport")
        
        try:
            # Read cartridge header first
            print("Reading cartridge header...")
            header_data = bytearray()
            
            start_time = time.time()
            
            # Read first 0x150 bytes for header
            for addr in range(0x150):
                block = addr // 256
                offset = addr % 256
                bank_index = 0  # Bank 0
                
                read_cmd = CartAPI_Builder.read_byte(block, offset, bank_index)
                response = transport.send_command_fast(read_cmd)
                
                if len(response) >= 4:
                    # Parse response: cmd_id, addr_low, addr_high, data
                    data_byte = response[3]
                    header_data.append(data_byte)
                else:
                    print(f"✗ Invalid response at address {addr:04x}")
                    return False
                
                if addr % 64 == 63:  # Progress every 64 bytes
                    elapsed = time.time() - start_time
                    speed = (addr + 1) / elapsed if elapsed > 0 else 0
                    print(f"  Header progress: {addr + 1}/336 bytes ({speed:.1f} bytes/s)")
            
            elapsed = time.time() - start_time
            speed = len(header_data) / elapsed if elapsed > 0 else 0
            
            print(f"✓ Header read: {len(header_data)} bytes in {elapsed:.2f}s ({speed:.1f} bytes/s)")
            
            # Parse header info
            if len(header_data) >= 0x150:
                title_bytes = header_data[0x134:0x144]
                title = title_bytes.rstrip(b'\x00').decode('ascii', errors='ignore')
                rom_size_code = header_data[0x148]
                
                rom_sizes = {0x00: 32*1024, 0x01: 64*1024, 0x02: 128*1024, 0x03: 256*1024, 
                           0x04: 512*1024, 0x05: 1024*1024, 0x06: 2048*1024}
                rom_size = rom_sizes.get(rom_size_code, 512*1024)
                total_banks = rom_size // BANK_SIZE
                
                print(f"  Title: {title}")
                print(f"  ROM Size: {rom_size // 1024}KB ({total_banks} banks)")
                
                # Limit banks for testing
                if max_banks and total_banks > max_banks:
                    print(f"  Limiting to first {max_banks} banks for testing")
                    total_banks = max_banks
            else:
                print("✗ Invalid header")
                return False
            
            # Start full ROM dump
            print(f"\nDumping {total_banks} banks...")
            rom_data = bytearray(header_data)  # Start with header
            
            overall_start = time.time()
            
            # Read remaining banks
            for bank_num in range(total_banks):
                bank_start_time = time.time()
                print(f"\nBank {bank_num + 1}/{total_banks}:")
                
                # Set bank if needed (bank 0 is fixed, banks 1+ need switching)
                if bank_num >= 1:
                    set_bank_cmds = CartAPI_Builder.set_bank(bank_num)
                    for cmd in set_bank_cmds:
                        transport.send_command_fast(cmd)
                
                # Read bank data
                bank_data = bytearray()
                start_addr = 0x150 if bank_num == 0 else 0  # Skip header for bank 0
                
                for addr in range(start_addr, BANK_SIZE):
                    block = addr // 256
                    offset = addr % 256
                    bank_index = 1 if bank_num > 0 else 0
                    
                    read_cmd = CartAPI_Builder.read_byte(block, offset, bank_index)
                    response = transport.send_command_fast(read_cmd)
                    
                    if len(response) >= 4:
                        data_byte = response[3]
                        bank_data.append(data_byte)
                    else:
                        print(f"✗ Invalid response at bank {bank_num}, addr {addr:04x}")
                        return False
                    
                    # Progress every 1KB
                    if addr % 1024 == 1023:
                        elapsed = time.time() - bank_start_time
                        speed = (addr + 1 - start_addr) / elapsed if elapsed > 0 else 0
                        print(f"  {addr + 1 - start_addr:5d}/{BANK_SIZE - start_addr} bytes ({speed:.1f} bytes/s)")
                
                rom_data.extend(bank_data)
                
                bank_elapsed = time.time() - bank_start_time
                bank_speed = len(bank_data) / bank_elapsed if bank_elapsed > 0 else 0
                print(f"  ✓ Bank {bank_num + 1} complete: {len(bank_data)} bytes in {bank_elapsed:.2f}s ({bank_speed:.1f} bytes/s)")
            
            # Save ROM
            output_path = Path(output_file)
            with open(output_path, 'wb') as f:
                f.write(rom_data)
            
            total_elapsed = time.time() - overall_start
            total_speed = len(rom_data) / total_elapsed if total_elapsed > 0 else 0
            
            print(f"\n✓ ROM dump complete!")
            print(f"  File: {output_path}")
            print(f"  Size: {len(rom_data)} bytes ({len(rom_data) // 1024} KB)")
            print(f"  Time: {total_elapsed:.1f} seconds")
            print(f"  Speed: {total_speed:.1f} bytes/s ({total_speed * 60:.0f} bytes/min)")
            
            if total_banks < rom_size // BANK_SIZE:
                full_time_estimate = total_elapsed * (rom_size // BANK_SIZE) / total_banks
                print(f"  Estimated full ROM time: {full_time_estimate / 60:.1f} minutes")
            
            return True
            
        finally:
            transport.disconnect()
            print("Disconnected")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Fast ROM Dumper")
    parser.add_argument('output', help='Output ROM file')
    parser.add_argument('--max-banks', type=int, default=2, help='Max banks to read (for testing)')
    parser.add_argument('--full', action='store_true', help='Read full ROM (ignore max-banks)')
    
    args = parser.parse_args()
    
    max_banks = None if args.full else args.max_banks
    
    success = fast_dump_rom(args.output, max_banks)
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
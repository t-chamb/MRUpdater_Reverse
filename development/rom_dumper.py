#!/usr/bin/env python3
"""
ROM Dumper for ModRetro Chromatic
Dumps the complete ROM from a Game Boy cartridge inserted in the Chromatic device
"""

import sys
import time
import logging
import argparse
from pathlib import Path

# Add the source directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

def setup_logging(debug=False):
    """Set up logging configuration"""
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def get_rom_size_from_header(header_data):
    """Parse ROM size from cartridge header"""
    if len(header_data) < 0x150:
        return None
    
    rom_size_code = header_data[0x148]
    rom_sizes = {
        0x00: 32 * 1024,    # 32KB (2 banks)
        0x01: 64 * 1024,    # 64KB (4 banks)
        0x02: 128 * 1024,   # 128KB (8 banks)
        0x03: 256 * 1024,   # 256KB (16 banks)
        0x04: 512 * 1024,   # 512KB (32 banks)
        0x05: 1024 * 1024,  # 1MB (64 banks)
        0x06: 2048 * 1024,  # 2MB (128 banks)
        0x07: 4096 * 1024,  # 4MB (256 banks)
        0x08: 8192 * 1024,  # 8MB (512 banks)
    }
    
    return rom_sizes.get(rom_size_code, 512 * 1024)  # Default to 512KB

def get_cartridge_title(header_data):
    """Extract cartridge title from header"""
    if len(header_data) < 0x150:
        return "Unknown"
    
    # Title is at 0x134-0x143 (16 bytes)
    title_bytes = header_data[0x134:0x144]
    # Remove null bytes and decode
    title = title_bytes.rstrip(b'\x00').decode('ascii', errors='ignore')
    return title if title else "Unknown"

def read_bank_optimized(session, bank_num):
    """Optimized bank reading - just use the existing session method for now"""
    from cartclinic.consts import BANK_SIZE
    
    try:
        print(f"  Reading bank {bank_num + 1}...", end="", flush=True)
        bank_data = session.read_bank(bank_num)
        print(" ✓")
        return bank_data
        
    except Exception as e:
        print(f" ✗ Error: {e}")
        return None

def dump_rom(output_file, include_save=False, debug=False):
    """Dump the complete ROM from the Chromatic device"""
    
    print("=== ModRetro Chromatic ROM Dumper ===")
    print()
    
    try:
        # Import required modules
        from libpyretro.cartclinic.comms.session import Session
        from flashing_tool.chromatic import Chromatic
        from cartclinic.consts import BANK_SIZE
        
        # Initialize Chromatic device
        print("Connecting to Chromatic device...")
        chromatic = Chromatic()
        
        # Wait for device to be ready
        max_wait = 10  # seconds
        wait_time = 0
        while chromatic.current_state.id != 'ready_to_flash' and wait_time < max_wait:
            chromatic.update_status()
            time.sleep(0.5)
            wait_time += 0.5
            if debug:
                print(f"Device state: {chromatic.current_state.id}")
            
        if chromatic.current_state.id != 'ready_to_flash':
            print(f"✗ Device not ready. Current state: {chromatic.current_state.id}")
            print("Make sure the Chromatic device is connected and a cartridge is inserted.")
            return False
            
        print("✓ Chromatic device ready!")
        
        # Get the MCU port for communication
        mcu_port = chromatic.mcu_port
        if not mcu_port:
            print("✗ No MCU port found")
            return False
            
        if debug:
            print(f"Using MCU port: {mcu_port}")
        
        # Create session and connect
        session = Session()
        if not session.connect(port=mcu_port, baudrate=115200, timeout=5):
            print("✗ Failed to connect to Chromatic device")
            return False
            
        print("✓ Connected to device")
        
        try:
            # Read cartridge header first to determine ROM size
            print("Reading cartridge header...")
            header_data = session.read_header()
            if not header_data:
                print("✗ Failed to read cartridge header")
                return False
            
            # Parse cartridge info
            title = get_cartridge_title(header_data)
            rom_size = get_rom_size_from_header(header_data)
            total_banks = rom_size // BANK_SIZE
            
            print(f"✓ Cartridge detected: {title}")
            print(f"  ROM Size: {rom_size // 1024}KB ({total_banks} banks)")
            print()
            
            # Start ROM dump
            print(f"Dumping ROM to: {output_file}")
            rom_data = bytearray()
            
            start_time = time.time()
            
            # Use optimized bank reading
            for bank_num in range(total_banks):
                print(f"\nReading bank {bank_num + 1}/{total_banks}...")
                
                # Read bank with optimized method
                bank_data = read_bank_optimized(session, bank_num)
                if not bank_data:
                    print(f"✗ Failed to read bank {bank_num}")
                    return False
                
                if len(bank_data) != BANK_SIZE:
                    print(f"✗ Bank {bank_num} returned unexpected size: {len(bank_data)}")
                    return False
                
                rom_data.extend(bank_data)
                
                # Progress indicator
                progress = (bank_num + 1) / total_banks * 100
                elapsed = time.time() - start_time
                if elapsed > 0:
                    speed = (bank_num + 1) * BANK_SIZE / elapsed / 1024  # KB/s
                    print(f"Progress: {progress:5.1f}% - {speed:.1f} KB/s")
                else:
                    print(f"Progress: {progress:5.1f}%")
            
            print()  # New line after progress
            
            # Save ROM to file
            output_path = Path(output_file)
            with open(output_path, 'wb') as f:
                f.write(rom_data)
            
            elapsed_time = time.time() - start_time
            total_size_kb = len(rom_data) / 1024
            avg_speed = total_size_kb / elapsed_time if elapsed_time > 0 else 0
            
            print(f"✓ ROM dump completed!")
            print(f"  File: {output_path}")
            print(f"  Size: {len(rom_data)} bytes ({total_size_kb:.1f} KB)")
            print(f"  Time: {elapsed_time:.1f} seconds")
            print(f"  Speed: {avg_speed:.1f} KB/s")
            
            # Validate ROM
            print("\nValidating ROM...")
            if len(rom_data) >= 0x150:
                # Check header checksum
                header_checksum = 0
                for i in range(0x134, 0x14D):
                    header_checksum = (header_checksum - rom_data[i] - 1) & 0xFF
                
                expected_checksum = rom_data[0x14D]
                header_valid = (header_checksum == expected_checksum)
                
                print(f"  Header checksum: {'✓ Valid' if header_valid else '✗ Invalid'}")
                
                # Check global checksum
                global_checksum = 0
                for i, byte in enumerate(rom_data):
                    if i not in (0x14E, 0x14F):  # Skip global checksum bytes
                        global_checksum = (global_checksum + byte) & 0xFFFF
                
                expected_global = (rom_data[0x14E] << 8) | rom_data[0x14F]
                global_valid = (global_checksum == expected_global)
                
                print(f"  Global checksum: {'✓ Valid' if global_valid else '✗ Invalid'} (0x{global_checksum:04X})")
            
            # Read save data if requested
            if include_save:
                print("\nReading save data...")
                save_data = session.read_save_data()
                if save_data:
                    save_path = output_path.with_suffix('.sav')
                    with open(save_path, 'wb') as f:
                        f.write(save_data)
                    print(f"✓ Save data saved: {save_path} ({len(save_data)} bytes)")
                else:
                    print("  No save data found")
            
            # Create info file
            info_path = output_path.with_suffix('.txt')
            with open(info_path, 'w') as f:
                f.write(f"ROM Dump Information\n")
                f.write(f"===================\n\n")
                f.write(f"Game Title: {title}\n")
                f.write(f"ROM Size: {len(rom_data)} bytes ({total_size_kb:.1f} KB)\n")
                f.write(f"Banks: {total_banks}\n")
                f.write(f"Dump Time: {elapsed_time:.1f} seconds\n")
                f.write(f"Average Speed: {avg_speed:.1f} KB/s\n")
                if len(rom_data) >= 0x150:
                    f.write(f"Header Checksum: {'Valid' if header_valid else 'Invalid'}\n")
                    f.write(f"Global Checksum: {'Valid' if global_valid else 'Invalid'} (0x{global_checksum:04X})\n")
                f.write(f"\nDumped with ModRetro Chromatic ROM Dumper\n")
            
            print(f"✓ Info file saved: {info_path}")
            
            return True
            
        finally:
            # Always disconnect
            session.disconnect()
            if debug:
                print("Disconnected from device")
        
    except Exception as e:
        print(f"✗ Error during ROM dump: {e}")
        if debug:
            import traceback
            traceback.print_exc()
        return False

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="ROM Dumper for ModRetro Chromatic",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s my_game.gb
  %(prog)s --save-data tetris.gb
  %(prog)s --debug pokemon.gb
        """
    )
    
    parser.add_argument(
        'output',
        help='Output ROM file (e.g., game.gb)'
    )
    
    parser.add_argument(
        '--save-data',
        action='store_true',
        help='Also dump save data to .sav file'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug output'
    )
    
    args = parser.parse_args()
    
    # Set up logging
    setup_logging(args.debug)
    
    # Validate output file extension
    output_path = Path(args.output)
    if output_path.suffix.lower() not in ['.gb', '.gbc']:
        print("Warning: Output file should have .gb or .gbc extension")
        response = input("Continue anyway? (y/N): ")
        if response.lower() != 'y':
            return 1
    
    # Run the ROM dump
    success = dump_rom(args.output, args.save_data, args.debug)
    
    if success:
        print("\n🎉 ROM dump completed successfully!")
        return 0
    else:
        print("\n💥 ROM dump failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
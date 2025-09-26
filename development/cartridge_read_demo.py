#!/usr/bin/env python3
"""
MRUpdater Cartridge Read Demo
Demonstrates the cartridge reading functionality with a simple CLI interface
"""

import sys
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
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def create_mock_session(rom_size_kb=512, has_save_data=True):
    """Create a mock session for demonstration"""
    from libpyretro.cartclinic.comms.session import Session
    from cartclinic.consts import BANK_SIZE
    
    class MockSession(Session):
        def __init__(self, rom_size_kb, has_save_data):
            super().__init__()
            self._connected = True
            self.bank_count = rom_size_kb // 16  # 16KB per bank
            self.has_save_data = has_save_data
            
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
            # Create realistic Game Boy ROM data
            bank_data = bytearray(BANK_SIZE)
            
            if bank_num == 0:
                # Bank 0 - ROM header
                bank_data[0x100:0x104] = b'\x00\xC3\x50\x01'  # NOP; JP $0150
                bank_data[0x134:0x144] = b"DEMO CART\x00\x00\x00\x00\x00\x00\x00"  # Title
                bank_data[0x147] = 0x01  # MBC1
                bank_data[0x148] = {32: 0x01, 64: 0x02, 128: 0x03, 256: 0x04, 512: 0x05, 1024: 0x06}.get(rom_size_kb, 0x05)
                bank_data[0x149] = 0x02 if self.has_save_data else 0x00  # 8KB RAM or no RAM
                bank_data[0x14A] = 0x01  # Japanese
                bank_data[0x14B] = 0x33  # Old licensee code
                bank_data[0x14C] = 0x00  # ROM version
                
                # Calculate header checksum
                checksum = 0
                for i in range(0x134, 0x14D):
                    checksum = (checksum - bank_data[i] - 1) & 0xFF
                bank_data[0x14D] = checksum
            else:
                # Other banks - fill with pattern
                for i in range(BANK_SIZE):
                    bank_data[i] = (bank_num + i) & 0xFF
                    
            return bytes(bank_data)
            
        def get_cartridge_info(self):
            return {
                'title': 'DEMO CART',
                'type': 'MBC1',
                'rom_size': self.bank_count * BANK_SIZE,
                'ram_size': 8192 if self.has_save_data else 0,
                'checksum': 0x1234
            }
            
        def read_header(self):
            # Return the first 0x150 bytes of bank 0
            bank_0 = self.read_bank(0)
            return bank_0[:0x150] if bank_0 else None
            
        def read_save_data(self):
            if not self.has_save_data:
                return None
            # Mock 8KB save data
            save_data = bytearray(8192)
            save_data[:4] = b"SAVE"
            # Fill with pattern
            for i in range(4, 8192):
                save_data[i] = i & 0xFF
            return bytes(save_data)
    
    return MockSession(rom_size_kb, has_save_data)

def demo_cartridge_read(args):
    """Demonstrate cartridge reading"""
    print(f"=== MRUpdater Cartridge Read Demo ===")
    print(f"Connecting to real Chromatic device...")
    print(f"Output File: {args.output}")
    print()
    
    try:
        from cartclinic.cartridge_read import read_cartridge_helper
        from libpyretro.cartclinic.comms.session import Session
        from flashing_tool.chromatic import Chromatic
        
        # Connect to real Chromatic device
        print("Initializing Chromatic device...")
        chromatic = Chromatic()
        
        # Wait for device to be ready
        import time
        max_wait = 10  # seconds
        wait_time = 0
        while chromatic.current_state.id != 'ready_to_flash' and wait_time < max_wait:
            chromatic.update_status()
            time.sleep(0.5)
            wait_time += 0.5
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
            
        print(f"Using MCU port: {mcu_port}")
        
        # Create real session
        session = Session()
        if not session.connect(port=mcu_port, baudrate=115200, timeout=5):
            print("✗ Failed to connect to Chromatic device")
            return False
            
        print("✓ Connected to Chromatic device")
        
        # Progress tracking
        def progress_callback(progress, message=""):
            if message:
                print(f"\r{message} ({progress}%)", end="", flush=True)
            else:
                print(f"\rProgress: {progress}%", end="", flush=True)
        
        print("Starting cartridge read...")
        
        try:
            # Perform the read
            result = read_cartridge_helper(
                session=session,
                animation=None,
                detection_thread=None,
                emit_progress=progress_callback,
                progress_callback=None,
                cancellation_token=None,
                include_save_data=args.save_data
            )
            
            print()  # New line after progress
            
        finally:
            # Always disconnect
            session.disconnect()
            print("Disconnected from device")
        
        if result:
            print("✓ Cartridge read completed successfully!")
            
            # Display results
            rom_data = result.get('rom_data', b'')
            save_data = result.get('save_data', None)
            cartridge_info = result.get('cartridge_info', {})
            checksum_valid = result.get('checksum_valid', False)
            
            print(f"  ROM Size: {len(rom_data)} bytes ({len(rom_data) // 1024}KB)")
            print(f"  Save Size: {len(save_data) if save_data else 0} bytes")
            print(f"  Title: {cartridge_info.get('title', 'Unknown')}")
            print(f"  Type: {cartridge_info.get('type', 'Unknown')}")
            print(f"  Checksum Valid: {'✓' if checksum_valid else '✗'}")
            
            # Save to file if requested
            if args.output:
                output_path = Path(args.output)
                
                # Save ROM
                rom_path = output_path.with_suffix('.gb')
                with open(rom_path, 'wb') as f:
                    f.write(rom_data)
                print(f"  ROM saved to: {rom_path}")
                
                # Save save data if present
                if save_data:
                    save_path = output_path.with_suffix('.sav')
                    with open(save_path, 'wb') as f:
                        f.write(save_data)
                    print(f"  Save data saved to: {save_path}")
                
                # Save info as text
                info_path = output_path.with_suffix('.txt')
                with open(info_path, 'w') as f:
                    f.write(f"Cartridge Information\n")
                    f.write(f"====================\n")
                    f.write(f"Title: {cartridge_info.get('title', 'Unknown')}\n")
                    f.write(f"Type: {cartridge_info.get('type', 'Unknown')}\n")
                    f.write(f"ROM Size: {len(rom_data)} bytes ({len(rom_data) // 1024}KB)\n")
                    f.write(f"Save Size: {len(save_data) if save_data else 0} bytes\n")
                    f.write(f"Checksum Valid: {'Yes' if checksum_valid else 'No'}\n")
                print(f"  Info saved to: {info_path}")
            
            return True
        else:
            print("✗ Cartridge read failed!")
            return False
            
    except Exception as e:
        print(f"✗ Error during cartridge read: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        return False

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="MRUpdater Cartridge Read Demo",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --output my_cartridge
  %(prog)s --save-data --output game_with_save --debug
  %(prog)s --help
        """
    )
    
    # ROM size will be auto-detected from the cartridge
    
    parser.add_argument(
        '--save-data',
        action='store_true',
        help='Include save data in the read'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        help='Output file prefix (will create .gb, .sav, .txt files)'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug logging'
    )
    
    args = parser.parse_args()
    
    # Set up logging
    setup_logging(args.debug)
    
    # Run the demo
    success = demo_cartridge_read(args)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
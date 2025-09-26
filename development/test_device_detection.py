#!/usr/bin/env python3
"""
Test script to check if Chromatic device can be detected
"""

import sys
import time
from flashing_tool.chromatic import Chromatic

def test_device_detection():
    print("=== Chromatic Device Detection Test ===")
    
    try:
        # Create Chromatic instance
        print("Creating Chromatic instance...")
        chromatic = Chromatic()
        print("✓ Chromatic instance created successfully")
        
        # Check for FPGA device
        print("\nChecking for FPGA device...")
        fpga_device = chromatic.fpga
        if fpga_device:
            print(f"✓ FPGA device detected: {fpga_device}")
            try:
                print(f"  - Vendor ID: 0x{fpga_device.idVendor:04x}")
                print(f"  - Product ID: 0x{fpga_device.idProduct:04x}")
                if hasattr(fpga_device, 'manufacturer'):
                    print(f"  - Manufacturer: {fpga_device.manufacturer}")
                if hasattr(fpga_device, 'product'):
                    print(f"  - Product: {fpga_device.product}")
            except Exception as e:
                print(f"  - Error reading device info: {e}")
        else:
            print("✗ No FPGA device detected")
            
        # Check for MCU port
        print("\nChecking for MCU port...")
        mcu_port = chromatic.mcu_port
        if mcu_port:
            print(f"✓ MCU port detected: {mcu_port}")
        else:
            print("✗ No MCU port detected")
            
        # Check current state
        print(f"\nCurrent state: {chromatic.current_state}")
        
        # Test device polling for a few seconds
        print("\nTesting device polling for 5 seconds...")
        start_time = time.time()
        while time.time() - start_time < 5:
            try:
                chromatic.update_status()
                time.sleep(1)
                print(f"  State: {chromatic.current_state.id}")
            except Exception as e:
                print(f"  Error during status update: {e}")
                
        print("\n=== Test Complete ===")
        
    except Exception as e:
        print(f"✗ Error during device detection test: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    return True

if __name__ == "__main__":
    success = test_device_detection()
    sys.exit(0 if success else 1)
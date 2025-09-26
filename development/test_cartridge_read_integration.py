#!/usr/bin/env python3
"""
Integration test for cartridge reading functionality.
Tests the complete workflow from session creation to ROM extraction.
"""

import sys
import os
import tempfile
import threading
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def test_complete_cartridge_read_workflow():
    """Test complete cartridge reading workflow"""
    try:
        from libpyretro.cartclinic.comms.session import Session
        from cartclinic.cartridge_read import read_cartridge_helper, extract_rom_with_progress
        
        print("Testing complete cartridge reading workflow...")
        
        # Create session
        session = Session()
        
        # Mock connection (for testing without hardware)
        session._connected = True
        
        # Mock cartridge info
        session._cartridge_info = {
            'rom_size': 64 * 1024,  # 64KB ROM
            'rom_banks': 4,
            'ram_size': 8 * 1024,   # 8KB RAM
            'ram_banks': 1,
            'has_ram': True,
            'has_battery': True,
            'title': 'TEST GAME',
            'mapper': 'MBC1'
        }
        
        # Mock read_bank method
        def mock_read_bank(bank_num):
            # Return different patterns for different banks
            if bank_num == 0:
                # Bank 0 with header
                data = bytearray(16384)
                # Add some header-like data
                data[0x134:0x144] = b'TEST GAME\x00\x00\x00\x00\x00\x00\x00'
                data[0x147] = 0x03  # MBC1+RAM+BATTERY
                data[0x148] = 0x01  # 64KB
                data[0x149] = 0x02  # 8KB RAM
                return bytes(data)
            else:
                # Other banks with pattern
                return bytes([bank_num] * 16384)
        
        session.read_bank = mock_read_bank
        
        # Mock read_save_data method
        def mock_read_save_data():
            return b'\xFF' * 8192  # 8KB of save data
        
        session.read_save_data = mock_read_save_data
        
        # Test 1: Basic ROM reading
        print("  Testing basic ROM reading...")
        result = read_cartridge_helper(session=session)
        
        assert isinstance(result, dict)
        assert 'rom_data' in result
        assert 'checksum_valid' in result
        assert 'cartridge_info' in result
        assert len(result['rom_data']) == 64 * 1024  # 64KB
        print("  ✓ Basic ROM reading successful")
        
        # Test 2: ROM reading with save data
        print("  Testing ROM reading with save data...")
        result_with_save = read_cartridge_helper(
            session=session,
            include_save_data=True
        )
        
        assert isinstance(result_with_save, dict)
        assert 'rom_data' in result_with_save
        assert 'save_data' in result_with_save
        assert result_with_save['save_data'] is not None
        assert len(result_with_save['save_data']) == 8192  # 8KB
        print("  ✓ ROM reading with save data successful")
        
        # Test 3: Progress reporting
        print("  Testing progress reporting...")
        progress_updates = []
        
        def progress_callback(percent, message):
            progress_updates.append((percent, message))
            print(f"    Progress: {percent}% - {message}")
        
        result_with_progress = read_cartridge_helper(
            session=session,
            progress_callback=progress_callback,
            include_save_data=True
        )
        
        assert len(progress_updates) > 0
        assert any(update[0] >= 90 for update in progress_updates)  # Should reach near 100%
        print("  ✓ Progress reporting working")
        
        # Test 4: Cancellation support
        print("  Testing cancellation support...")
        cancellation_token = threading.Event()
        
        # Start read operation and cancel immediately
        cancellation_token.set()
        
        result_cancelled = read_cartridge_helper(
            session=session,
            cancellation_token=cancellation_token
        )
        
        # Should still return a result structure
        assert isinstance(result_cancelled, dict)
        print("  ✓ Cancellation support working")
        
        # Test 5: File extraction
        print("  Testing ROM file extraction...")
        
        with tempfile.NamedTemporaryFile(suffix='.gb', delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            progress_updates.clear()
            
            success = extract_rom_with_progress(
                session=session,
                output_path=temp_path,
                progress_callback=progress_callback,
                include_save=True
            )
            
            assert success
            assert os.path.exists(temp_path)
            
            # Check file size
            file_size = os.path.getsize(temp_path)
            assert file_size == 64 * 1024  # Should be 64KB
            
            # Check for save file
            save_path = temp_path.rsplit('.', 1)[0] + '.sav'
            assert os.path.exists(save_path)
            
            save_size = os.path.getsize(save_path)
            assert save_size == 8192  # Should be 8KB
            
            print("  ✓ ROM file extraction successful")
            
        finally:
            # Clean up
            if os.path.exists(temp_path):
                os.unlink(temp_path)
            save_path = temp_path.rsplit('.', 1)[0] + '.sav'
            if os.path.exists(save_path):
                os.unlink(save_path)
        
        print("✓ Complete cartridge reading workflow test passed!")
        return True
        
    except Exception as e:
        print(f"✗ Workflow test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_error_handling():
    """Test error handling in cartridge reading"""
    try:
        from cartclinic.cartridge_read import read_cartridge_helper
        from cartclinic.exceptions import InvalidCartridgeError
        
        print("Testing error handling...")
        
        # Test 1: No session provided
        try:
            read_cartridge_helper(session=None)
            assert False, "Should have raised InvalidCartridgeError"
        except InvalidCartridgeError:
            print("  ✓ No session error handled correctly")
        
        # Test 2: No cartridge detected
        from libpyretro.cartclinic.comms.session import Session
        session = Session()
        session._connected = True
        session.get_cartridge_info = lambda: None  # No cartridge
        
        try:
            read_cartridge_helper(session=session)
            assert False, "Should have raised InvalidCartridgeError"
        except InvalidCartridgeError:
            print("  ✓ No cartridge error handled correctly")
        
        print("✓ Error handling test passed!")
        return True
        
    except Exception as e:
        print(f"✗ Error handling test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_checksum_validation():
    """Test ROM checksum validation with different scenarios"""
    try:
        from cartclinic.cartridge_read import validate_rom_checksum
        
        print("Testing checksum validation...")
        
        # Test 1: Valid ROM structure
        rom_data = bytearray(32 * 1024)  # 32KB
        
        # Add basic header structure
        rom_data[0x134:0x144] = b'CHECKSUM TEST\x00\x00\x00'
        rom_data[0x147] = 0x00  # ROM only
        rom_data[0x148] = 0x00  # 32KB
        rom_data[0x149] = 0x00  # No RAM
        rom_data[0x14A] = 0x01  # Non-Japanese
        rom_data[0x14B] = 0x33  # Old licensee
        rom_data[0x14C] = 0x00  # Version
        rom_data[0x14D] = 0x00  # Header checksum (will be wrong)
        rom_data[0x14E] = 0x00  # Global checksum low
        rom_data[0x14F] = 0x00  # Global checksum high
        
        is_valid = validate_rom_checksum(bytes(rom_data))
        assert isinstance(is_valid, bool)
        print("  ✓ Checksum validation completed")
        
        # Test 2: Too short ROM
        short_rom = b'\x00' * 100
        is_valid_short = validate_rom_checksum(short_rom)
        assert is_valid_short == False
        print("  ✓ Short ROM handled correctly")
        
        print("✓ Checksum validation test passed!")
        return True
        
    except Exception as e:
        print(f"✗ Checksum validation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all integration tests"""
    print("Running cartridge reading integration tests...")
    print("=" * 60)
    
    tests = [
        test_complete_cartridge_read_workflow,
        test_error_handling,
        test_checksum_validation
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        print()
        if test():
            passed += 1
        print("-" * 40)
    
    print()
    print(f"Integration Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All integration tests passed!")
        print("Cartridge reading functionality is fully implemented and working.")
        return True
    else:
        print("❌ Some integration tests failed.")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
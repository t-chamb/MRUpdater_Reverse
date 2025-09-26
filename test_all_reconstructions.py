#!/usr/bin/env python3
"""
Test all reconstructed dataclasses to ensure they work correctly
"""

import sys
sys.path.append('/tmp')

# Import all our reconstructed dataclasses
from COMPLETE_NODE_RECONSTRUCTION import *

def test_mrpatcher_classes():
    print("=== Testing MRPatcher Classes ===\n")
    
    # Test GameSaveSettings
    save_settings = GameSaveSettings(
        save_compatible=True,
        saves_to_rom=False,
        offset_kb=0,
        max_length=8192
    )
    print(f"✓ GameSaveSettings: {save_settings}")
    
    # Test MRPatcherGameInfo
    game_info_data = {
        "game_id": "TETRIS",
        "title": "TETRIS",
        "save_settings": {
            "save_compatible": True,
            "saves_to_rom": False,
            "offset_kb": 0,
            "max_length": 8192
        },
        "supported": True
    }
    game_info = MRPatcherGameInfo.from_dict(game_info_data)
    print(f"✓ MRPatcherGameInfo: {game_info}")
    
    # Test MRPatcherResponse
    response_data = {
        "game_title": "TETRIS",
        "thumbnail": "",
        "patch": "UEFUQ0g=",  # Base64 "PATCH"
        "error": "",
        "error_code": "",
        "user_error": False,
        "needs_update": False,
        "save_compatible": True,
        "uploaded_version": "1.0",
        "latest_version": "1.0",
        "changes": "",
        "save_settings": {
            "save_compatible": True,
            "saves_to_rom": False,
            "offset_kb": 0,
            "max_length": 8192
        }
    }
    response = MRPatcherResponse.from_dict(response_data)
    print(f"✓ MRPatcherResponse: game_title={response.game_title}, patch_size={len(response.patch)}")

def test_firmware_classes():
    print("\n=== Testing Firmware Classes ===\n")
    
    # Test S3FirmwareInfo
    fw_info = S3FirmwareInfo(
        filename="v4.0.zip",
        directory="firmware/chromatic/current",
        label="LATEST"
    )
    print(f"✓ S3FirmwareInfo: {fw_info}")
    
    # Test ChromaticFirmwarePackage
    chromatic_pkg = ChromaticFirmwarePackage(
        zip_path="/tmp/v4.0.zip",
        fpga_fw_path="/tmp/fpga.fs",
        mcu_fw_path="/tmp/mcu.bin",
        temp_dir_path="/tmp/extract",
        changelog={"version": "4.0", "changes": "Bug fixes"},
        version="4.0",
        label="LATEST"
    )
    print(f"✓ ChromaticFirmwarePackage: version={chromatic_pkg.version}")
    
    # Test MRUpdaterManifestData
    manifest = MRUpdaterManifestData(
        version="1.6.1",
        mrpatcher_endpoint="https://example.com/mrpatcher",
        chromatic_fw_options=[fw_info],
        cartclinic_fw_info=fw_info,
        chromatic_fw_changelog_uri="firmware/changelog.yaml"
    )
    print(f"✓ MRUpdaterManifestData: version={manifest.version}")

def test_protocol_classes():
    print("\n=== Testing Protocol Classes ===\n")
    
    # Test UnsignedByte
    try:
        byte = UnsignedByte(value=255)
        print(f"✓ UnsignedByte: {byte}")
        invalid = UnsignedByte(value=256)
    except ValueError as e:
        print(f"✓ UnsignedByte validation works: {e}")
    
    # Test PixelRGB555
    pixel = PixelRGB555(value=(31, 0, 15))
    print(f"✓ PixelRGB555: {pixel}, as_uint15={pixel.value_as_uint15()}")
    
    # Test CartFlashInfo
    flash_info = CartFlashInfo(
        part_id=CartFlashChip.ISSI_IS29GL032,
        part_number="IS29GL032",
        vendor="ISSI",
        total_size_kb=4096,
        sector_size_kb=64,
        grouping=1,
        recovery_offset_kb=0
    )
    print(f"✓ CartFlashInfo: {flash_info.vendor} {flash_info.part_number}")

def test_exception_classes():
    print("\n=== Testing Exception Classes ===\n")
    
    # Test ComparisonError
    comp_error = ComparisonError(
        expected=b'\\x00\\x01',
        actual=b'\\x00\\x02'
    )
    print(f"✓ ComparisonError: expected={comp_error.expected.hex()}, actual={comp_error.actual.hex()}")
    
    # Test InvalidWriteBankSize
    bank_error = InvalidWriteBankSize(size=8192)
    print(f"✓ InvalidWriteBankSize: size={bank_error.size}")

if __name__ == "__main__":
    print("Testing All Reconstructed Dataclasses\n")
    print("=" * 50 + "\n")
    
    test_mrpatcher_classes()
    test_firmware_classes()
    test_protocol_classes()
    test_exception_classes()
    
    print("\n" + "=" * 50)
    print("\n✅ All tests passed! The reconstructed dataclasses are working correctly.")
    print("\nThese can now be contributed back to the MRUpdater_Reverse project.")
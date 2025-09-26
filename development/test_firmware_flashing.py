#!/usr/bin/env python3
"""
Test script for firmware flashing functionality.
Tests the firmware download, validation, and flashing workflow.
"""

import sys
import logging
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

from flashing_tool.firmware_manager import FirmwareManager
from flashing_tool.fpga_flasher import FPGAFlasher
from flashing_tool.mcu_flasher import MCUFlasher
from flashing_tool.firmware_flasher import FirmwareFlasher, FirmwareFlashProgress
from flashing_tool.util import FlashOperation

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def test_firmware_manager():
    """Test firmware manager functionality"""
    logger.info("Testing FirmwareManager...")
    
    try:
        manager = FirmwareManager()
        
        # Test manifest loading
        logger.info("Loading firmware manifest...")
        manifest = manager.get_firmware_manifest()
        
        if manifest:
            logger.info(f"Manifest loaded successfully:")
            logger.info(f"  Latest version: {manifest.latest_version}")
            logger.info(f"  Available versions: {len(manifest.firmware_list)}")
            
            if manifest.firmware_list:
                latest_fw = manifest.firmware_list[0]
                logger.info(f"  Sample firmware: {latest_fw.version}")
                logger.info(f"    MCU binary: {latest_fw.mcu_binary_key}")
                logger.info(f"    FPGA bitstream: {latest_fw.fpga_bitstream_key}")
        else:
            logger.warning("Could not load firmware manifest")
        
        # Test cached versions
        cached_versions = manager.list_cached_versions()
        logger.info(f"Cached versions: {cached_versions}")
        
        # Test cache size
        cache_size = manager.get_cache_size()
        logger.info(f"Cache size: {cache_size} bytes")
        
        return True
        
    except Exception as e:
        logger.error(f"FirmwareManager test failed: {e}")
        return False

def test_fpga_flasher():
    """Test FPGA flasher functionality"""
    logger.info("Testing FPGAFlasher...")
    
    try:
        flasher = FPGAFlasher()
        
        # Test device detection
        logger.info("Detecting FPGA devices...")
        devices = flasher.detect_fpga_devices()
        
        if devices:
            logger.info(f"Detected {len(devices)} FPGA device(s):")
            for device in devices:
                logger.info(f"  - {device}")
        else:
            logger.info("No FPGA devices detected")
        
        # Test FPGA info
        fpga_info = flasher.get_fpga_info()
        if fpga_info:
            logger.info(f"FPGA info: {fpga_info}")
        
        return True
        
    except Exception as e:
        logger.error(f"FPGAFlasher test failed: {e}")
        return False

def test_mcu_flasher():
    """Test MCU flasher functionality"""
    logger.info("Testing MCUFlasher...")
    
    try:
        flasher = MCUFlasher()
        
        # Test device detection
        logger.info("Detecting ESP32 devices...")
        devices = flasher.detect_mcu_devices()
        
        if devices:
            logger.info(f"Detected {len(devices)} ESP32 device(s):")
            for device in devices:
                logger.info(f"  - {device}")
        else:
            logger.info("No ESP32 devices detected")
        
        # Test MCU info
        mcu_info = flasher.get_mcu_info()
        if mcu_info:
            logger.info(f"MCU info: {mcu_info}")
        
        return True
        
    except Exception as e:
        logger.error(f"MCUFlasher test failed: {e}")
        return False

def test_firmware_flasher():
    """Test integrated firmware flasher"""
    logger.info("Testing FirmwareFlasher...")
    
    try:
        flasher = FirmwareFlasher()
        
        # Test update check
        logger.info("Checking for updates...")
        comparison = flasher.check_for_updates()
        
        if comparison:
            logger.info(f"Update check result:")
            logger.info(f"  Current: MCU {comparison.current_version.mcu_version}, FPGA {comparison.current_version.fpga_version}")
            if comparison.available_version:
                logger.info(f"  Available: MCU {comparison.available_version.mcu_version}, FPGA {comparison.available_version.fpga_version}")
            logger.info(f"  Update available: {comparison.update_available}")
        else:
            logger.info("Could not check for updates (no device connected)")
        
        # Test available versions
        versions = flasher.get_available_versions()
        logger.info(f"Available versions: {versions[:5]}...")  # Show first 5
        
        # Test firmware info
        if versions:
            info = flasher.get_firmware_info(versions[0])
            if info:
                logger.info(f"Firmware info for {versions[0]}: {info}")
        
        # Test compatibility validation
        if versions:
            validation = flasher.validate_firmware_compatibility(versions[0])
            logger.info(f"Compatibility validation: {validation}")
        
        return True
        
    except Exception as e:
        logger.error(f"FirmwareFlasher test failed: {e}")
        return False

def progress_callback(progress: FirmwareFlashProgress):
    """Progress callback for testing"""
    logger.info(f"Progress: {progress.stage.value} - {progress.overall_progress:.1f}% - {progress.current_operation}")

def main():
    """Run all tests"""
    logger.info("Starting firmware flashing tests...")
    
    tests = [
        ("FirmwareManager", test_firmware_manager),
        ("FPGAFlasher", test_fpga_flasher),
        ("MCUFlasher", test_mcu_flasher),
        ("FirmwareFlasher", test_firmware_flasher),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        logger.info(f"\n{'='*50}")
        logger.info(f"Running {test_name} test...")
        logger.info(f"{'='*50}")
        
        try:
            results[test_name] = test_func()
        except Exception as e:
            logger.error(f"{test_name} test crashed: {e}")
            results[test_name] = False
    
    # Summary
    logger.info(f"\n{'='*50}")
    logger.info("Test Results Summary:")
    logger.info(f"{'='*50}")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results.items():
        status = "PASS" if result else "FAIL"
        logger.info(f"{test_name}: {status}")
        if result:
            passed += 1
    
    logger.info(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("All tests passed! ✅")
        return 0
    else:
        logger.error("Some tests failed! ❌")
        return 1

if __name__ == "__main__":
    sys.exit(main())
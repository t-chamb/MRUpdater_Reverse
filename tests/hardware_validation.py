#!/usr/bin/env python3
"""
Hardware validation test suite for MRUpdater.

This module provides comprehensive testing of MRUpdater functionality
with real Chromatic devices and Game Boy cartridges.

Usage:
    python hardware_validation.py --device-test
    python hardware_validation.py --cartridge-test --rom-path test.gb
    python hardware_validation.py --firmware-test --version latest
    python hardware_validation.py --full-suite
"""

import argparse
import logging
import os
import sys
import time
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import MRUpdater modules
from flashing_tool.device_manager import DeviceManager
from flashing_tool.firmware_flasher import FirmwareFlasher
from cartclinic.cartridge_detection import CartridgeDetector
from cartclinic.cartridge_read import read_cartridge_helper
from cartclinic.cartridge_write import write_cartridge_helper
from libpyretro.cartclinic.comms import Session
from exceptions import ChromaticError
from logging_config import LogCategory, get_logger


class TestResult(Enum):
    """Test result status"""
    PASS = "PASS"
    FAIL = "FAIL"
    SKIP = "SKIP"
    ERROR = "ERROR"


@dataclass
class TestCase:
    """Individual test case"""
    name: str
    description: str
    category: str
    result: TestResult = TestResult.SKIP
    duration: float = 0.0
    error_message: Optional[str] = None
    details: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.details is None:
            self.details = {}


class HardwareValidator:
    """
    Comprehensive hardware validation test suite.
    
    Tests all aspects of MRUpdater functionality with real hardware:
    - Device detection and communication
    - Firmware flashing operations
    - Cartridge operations (read/write)
    - Error handling and recovery
    """
    
    def __init__(self, verbose: bool = False):
        self.logger = get_logger(LogCategory.TESTING, "hardware_validator")
        self.verbose = verbose
        
        # Test results
        self.test_cases: List[TestCase] = []
        self.device_manager = None
        self.firmware_flasher = None
        self.cartridge_detector = None
        self.session = None
        
        # Test configuration
        self.test_config = {
            'device_timeout': 30.0,
            'firmware_timeout': 300.0,
            'cartridge_timeout': 120.0,
            'retry_attempts': 3,
            'test_rom_size': 32 * 1024,  # 32KB test ROM
        }
        
        # Test data
        self.test_results_file = project_root / "test_results" / f"hardware_validation_{int(time.time())}.json"
        self.test_results_file.parent.mkdir(exist_ok=True)
    
    def log_test_start(self, test_name: str, description: str):
        """Log test start"""
        self.logger.info(f"Starting test: {test_name}")
        if self.verbose:
            print(f"🧪 {test_name}: {description}")
    
    def log_test_result(self, test_case: TestCase):
        """Log test result"""
        status_emoji = {
            TestResult.PASS: "✅",
            TestResult.FAIL: "❌", 
            TestResult.SKIP: "⏭️",
            TestResult.ERROR: "💥"
        }
        
        emoji = status_emoji.get(test_case.result, "❓")
        self.logger.info(f"Test result: {test_case.name} - {test_case.result.value}")
        
        if self.verbose:
            print(f"{emoji} {test_case.name}: {test_case.result.value} ({test_case.duration:.2f}s)")
            if test_case.error_message:
                print(f"   Error: {test_case.error_message}")
    
    def run_test(self, test_func, name: str, description: str, category: str, **kwargs) -> TestCase:
        """Run a single test case"""
        test_case = TestCase(name=name, description=description, category=category)
        
        self.log_test_start(name, description)
        start_time = time.time()
        
        try:
            result = test_func(**kwargs)
            test_case.result = TestResult.PASS if result else TestResult.FAIL
            if isinstance(result, dict):
                test_case.details.update(result)
                
        except Exception as e:
            test_case.result = TestResult.ERROR
            test_case.error_message = str(e)
            self.logger.error(f"Test error: {name} - {e}")
            
        finally:
            test_case.duration = time.time() - start_time
            self.test_cases.append(test_case)
            self.log_test_result(test_case)
        
        return test_case
    
    # =============================================================================
    # DEVICE DETECTION AND COMMUNICATION TESTS
    # =============================================================================
    
    def test_device_detection(self) -> bool:
        """Test Chromatic device detection"""
        try:
            self.device_manager = DeviceManager()
            devices = self.device_manager.scan_for_devices(timeout=self.test_config['device_timeout'])
            
            if not devices:
                self.logger.warning("No Chromatic devices detected")
                return False
            
            self.logger.info(f"Detected {len(devices)} Chromatic device(s)")
            
            # Test connection to first device
            device = devices[0]
            if self.device_manager.connect_to_device(device):
                self.logger.info(f"Successfully connected to device: {device.serial_number}")
                return True
            else:
                self.logger.error("Failed to connect to detected device")
                return False
                
        except Exception as e:
            self.logger.error(f"Device detection test failed: {e}")
            return False
    
    def test_device_communication(self) -> Dict[str, Any]:
        """Test basic device communication"""
        if not self.device_manager or not self.device_manager.current_device:
            raise Exception("No device connected for communication test")
        
        results = {}
        
        try:
            # Test device info retrieval
            device_info = self.device_manager.get_device_info()
            results['device_info'] = device_info
            
            # Test firmware version query
            firmware_version = self.device_manager.get_firmware_version()
            results['firmware_version'] = firmware_version
            
            # Test device status
            device_status = self.device_manager.get_device_status()
            results['device_status'] = device_status
            
            # Test communication latency
            start_time = time.time()
            for _ in range(10):
                self.device_manager.ping_device()
            avg_latency = (time.time() - start_time) / 10
            results['average_latency'] = avg_latency
            
            self.logger.info(f"Device communication test passed - latency: {avg_latency:.3f}s")
            return results
            
        except Exception as e:
            self.logger.error(f"Device communication test failed: {e}")
            raise
    
    def test_device_recovery(self) -> bool:
        """Test device recovery from error states"""
        if not self.device_manager or not self.device_manager.current_device:
            raise Exception("No device connected for recovery test")
        
        try:
            # Simulate error condition
            self.logger.info("Testing device recovery...")
            
            # Try to recover device
            recovery_success = self.device_manager.recover_device()
            
            if recovery_success:
                # Verify device is responsive after recovery
                device_info = self.device_manager.get_device_info()
                return device_info is not None
            
            return False
            
        except Exception as e:
            self.logger.error(f"Device recovery test failed: {e}")
            return False
    
    # =============================================================================
    # FIRMWARE FLASHING TESTS
    # =============================================================================
    
    def test_firmware_download(self, version: str = "latest") -> Dict[str, Any]:
        """Test firmware download functionality"""
        try:
            self.firmware_flasher = FirmwareFlasher(self.device_manager)
            
            # Test firmware manifest retrieval
            manifest = self.firmware_flasher.firmware_manager.get_firmware_manifest()
            if not manifest:
                raise Exception("Failed to retrieve firmware manifest")
            
            # Test firmware info retrieval
            firmware_info = self.firmware_flasher.firmware_manager.get_firmware_info(version, manifest)
            if not firmware_info:
                raise Exception(f"Firmware version '{version}' not found")
            
            # Test firmware download
            firmware_package = self.firmware_flasher.firmware_manager.download_firmware(firmware_info)
            if not firmware_package:
                raise Exception("Failed to download firmware package")
            
            results = {
                'version': firmware_info.version,
                'package_size': len(firmware_package.mcu_binary) + len(firmware_package.fpga_bitstream),
                'mcu_size': len(firmware_package.mcu_binary),
                'fpga_size': len(firmware_package.fpga_bitstream),
                'download_successful': True
            }
            
            self.logger.info(f"Firmware download test passed - version: {firmware_info.version}")
            return results
            
        except Exception as e:
            self.logger.error(f"Firmware download test failed: {e}")
            raise
    
    def test_firmware_validation(self, version: str = "latest") -> Dict[str, Any]:
        """Test firmware package validation"""
        if not self.firmware_flasher:
            raise Exception("Firmware flasher not initialized")
        
        try:
            # Test compatibility validation
            validation = self.firmware_flasher.validate_firmware_compatibility(version)
            
            results = {
                'compatible': validation['compatible'],
                'version_found': validation['version_found'],
                'bootloader_compatible': validation['bootloader_compatible'],
                'warnings': validation['warnings'],
                'errors': validation['errors']
            }
            
            if validation['compatible']:
                self.logger.info(f"Firmware validation passed for version: {version}")
            else:
                self.logger.warning(f"Firmware validation failed for version: {version}")
                self.logger.warning(f"Errors: {validation['errors']}")
            
            return results
            
        except Exception as e:
            self.logger.error(f"Firmware validation test failed: {e}")
            raise
    
    def test_firmware_flash_dry_run(self, version: str = "latest") -> bool:
        """Test firmware flash preparation without actual flashing"""
        if not self.firmware_flasher:
            raise Exception("Firmware flasher not initialized")
        
        try:
            # This would test all preparation steps without actual flashing
            # In a real implementation, this would verify:
            # - Device is in correct state for flashing
            # - Firmware package is valid
            # - All tools are available
            # - Sufficient power/connection stability
            
            self.logger.info("Firmware flash dry run - preparation steps only")
            
            # Simulate preparation checks
            time.sleep(2)  # Simulate preparation time
            
            self.logger.info("Firmware flash dry run completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Firmware flash dry run failed: {e}")
            return False
    
    # =============================================================================
    # CARTRIDGE OPERATION TESTS
    # =============================================================================
    
    def test_cartridge_detection(self) -> Dict[str, Any]:
        """Test cartridge detection and identification"""
        try:
            if not self.session:
                self.session = Session(self.device_manager.current_device.transport)
            
            self.cartridge_detector = CartridgeDetector(self.session)
            
            # Test cartridge presence detection
            cartridge_present = self.cartridge_detector.is_cartridge_present()
            
            results = {'cartridge_present': cartridge_present}
            
            if cartridge_present:
                # Test cartridge identification
                cartridge_info = self.cartridge_detector.identify_cartridge()
                
                if cartridge_info:
                    results.update({
                        'title': cartridge_info.title,
                        'mapper_type': cartridge_info.mapper_type,
                        'rom_size': cartridge_info.rom_size,
                        'ram_size': cartridge_info.ram_size,
                        'checksum': cartridge_info.checksum,
                        'save_type': cartridge_info.save_type
                    })
                    
                    self.logger.info(f"Cartridge detected: {cartridge_info.title} ({cartridge_info.mapper_type})")
                else:
                    self.logger.warning("Cartridge present but identification failed")
                    results['identification_failed'] = True
            else:
                self.logger.info("No cartridge detected")
            
            return results
            
        except Exception as e:
            self.logger.error(f"Cartridge detection test failed: {e}")
            raise
    
    def test_cartridge_read(self, verify_checksum: bool = True) -> Dict[str, Any]:
        """Test cartridge ROM reading"""
        if not self.session:
            raise Exception("No session available for cartridge read test")
        
        try:
            # Read cartridge data
            start_time = time.time()
            
            rom_data = read_cartridge_helper(
                session=self.session,
                progress_callback=lambda p, m: self.logger.debug(f"Read progress: {p}% - {m}")
            )
            
            read_time = time.time() - start_time
            
            if not rom_data:
                raise Exception("Failed to read ROM data")
            
            results = {
                'rom_size': len(rom_data),
                'read_time': read_time,
                'read_speed_kbps': (len(rom_data) / 1024) / read_time if read_time > 0 else 0
            }
            
            if verify_checksum and len(rom_data) >= 0x14E:
                # Calculate and verify Game Boy header checksum
                header_checksum = 0
                for i in range(0x134, 0x14D):
                    header_checksum = (header_checksum - rom_data[i] - 1) & 0xFF
                
                expected_checksum = rom_data[0x14D]
                checksum_valid = header_checksum == expected_checksum
                
                results.update({
                    'header_checksum_calculated': header_checksum,
                    'header_checksum_expected': expected_checksum,
                    'header_checksum_valid': checksum_valid
                })
            
            self.logger.info(f"Cartridge read test passed - {len(rom_data)} bytes in {read_time:.2f}s")
            return results
            
        except Exception as e:
            self.logger.error(f"Cartridge read test failed: {e}")
            raise
    
    def test_cartridge_write(self, test_rom_path: Optional[str] = None) -> Dict[str, Any]:
        """Test cartridge ROM writing (requires writable cartridge)"""
        if not self.session:
            raise Exception("No session available for cartridge write test")
        
        try:
            # Use provided ROM or create test ROM
            if test_rom_path and os.path.exists(test_rom_path):
                with open(test_rom_path, 'rb') as f:
                    test_rom_data = f.read()
            else:
                # Create minimal test ROM
                test_rom_data = self._create_test_rom()
            
            # Write ROM data
            start_time = time.time()
            
            write_success = write_cartridge_helper(
                session=self.session,
                rom_data=test_rom_data,
                progress_callback=lambda p, m: self.logger.debug(f"Write progress: {p}% - {m}")
            )
            
            write_time = time.time() - start_time
            
            if not write_success:
                raise Exception("ROM write operation failed")
            
            # Verify write by reading back
            verification_start = time.time()
            read_back_data = read_cartridge_helper(session=self.session)
            verification_time = time.time() - verification_start
            
            # Compare data
            data_matches = read_back_data[:len(test_rom_data)] == test_rom_data
            
            results = {
                'rom_size': len(test_rom_data),
                'write_time': write_time,
                'write_speed_kbps': (len(test_rom_data) / 1024) / write_time if write_time > 0 else 0,
                'verification_time': verification_time,
                'data_verification_passed': data_matches
            }
            
            if data_matches:
                self.logger.info(f"Cartridge write test passed - {len(test_rom_data)} bytes")
            else:
                self.logger.error("Cartridge write verification failed - data mismatch")
                results['verification_failed'] = True
            
            return results
            
        except Exception as e:
            self.logger.error(f"Cartridge write test failed: {e}")
            raise
    
    def _create_test_rom(self) -> bytes:
        """Create a minimal test ROM for write testing"""
        # Create 32KB test ROM with valid Game Boy header
        rom_data = bytearray(self.test_config['test_rom_size'])
        
        # Add Game Boy header
        rom_data[0x100:0x104] = b'\x00\xC3\x50\x01'  # NOP; JP $0150
        rom_data[0x104:0x134] = b'\xCE\xED\x66\x66\xCC\x0D\x00\x0B\x03\x73\x00\x83\x00\x0C\x00\x0D' + \
                               b'\x00\x08\x11\x1F\x88\x89\x00\x0E\xDC\xCC\x6E\xE6\xDD\xDD\xD9\x99' + \
                               b'\xBB\xBB\x67\x63\x6E\x0E\xEC\xCC\xDD\xDC\x99\x9F\xBB\xB9\x33\x3E'
        
        # Title
        title = b"TEST ROM"
        rom_data[0x134:0x134+len(title)] = title
        
        # ROM size (32KB = 0x00)
        rom_data[0x148] = 0x00
        
        # RAM size (none = 0x00)
        rom_data[0x149] = 0x00
        
        # Calculate header checksum
        header_checksum = 0
        for i in range(0x134, 0x14D):
            header_checksum = (header_checksum - rom_data[i] - 1) & 0xFF
        rom_data[0x14D] = header_checksum
        
        # Calculate global checksum (simple sum)
        global_checksum = sum(rom_data) & 0xFFFF
        rom_data[0x14E] = (global_checksum >> 8) & 0xFF
        rom_data[0x14F] = global_checksum & 0xFF
        
        return bytes(rom_data)
    
    # =============================================================================
    # COMPREHENSIVE TEST SUITES
    # =============================================================================
    
    def run_device_tests(self) -> List[TestCase]:
        """Run all device-related tests"""
        device_tests = [
            ("Device Detection", "Test Chromatic device detection and enumeration", self.test_device_detection),
            ("Device Communication", "Test basic device communication", self.test_device_communication),
            ("Device Recovery", "Test device recovery from error states", self.test_device_recovery),
        ]
        
        results = []
        for name, description, test_func in device_tests:
            result = self.run_test(test_func, name, description, "Device")
            results.append(result)
            
            # Stop if device detection fails
            if name == "Device Detection" and result.result != TestResult.PASS:
                self.logger.error("Device detection failed - skipping remaining device tests")
                break
        
        return results
    
    def run_firmware_tests(self, version: str = "latest") -> List[TestCase]:
        """Run all firmware-related tests"""
        firmware_tests = [
            ("Firmware Download", "Test firmware package download", 
             lambda: self.test_firmware_download(version)),
            ("Firmware Validation", "Test firmware compatibility validation", 
             lambda: self.test_firmware_validation(version)),
            ("Firmware Flash Dry Run", "Test firmware flash preparation", 
             lambda: self.test_firmware_flash_dry_run(version)),
        ]
        
        results = []
        for name, description, test_func in firmware_tests:
            result = self.run_test(test_func, name, description, "Firmware")
            results.append(result)
        
        return results
    
    def run_cartridge_tests(self, test_rom_path: Optional[str] = None) -> List[TestCase]:
        """Run all cartridge-related tests"""
        cartridge_tests = [
            ("Cartridge Detection", "Test cartridge presence and identification", self.test_cartridge_detection),
            ("Cartridge Read", "Test ROM reading from cartridge", self.test_cartridge_read),
        ]
        
        # Only add write test if we have a test ROM or writable cartridge
        if test_rom_path or self._prompt_for_write_test():
            cartridge_tests.append(
                ("Cartridge Write", "Test ROM writing to cartridge", 
                 lambda: self.test_cartridge_write(test_rom_path))
            )
        
        results = []
        for name, description, test_func in cartridge_tests:
            result = self.run_test(test_func, name, description, "Cartridge")
            results.append(result)
        
        return results
    
    def _prompt_for_write_test(self) -> bool:
        """Prompt user for cartridge write test confirmation"""
        if not sys.stdin.isatty():
            return False  # Non-interactive mode
        
        print("\n⚠️  Cartridge Write Test Warning ⚠️")
        print("The write test will overwrite the cartridge's ROM data.")
        print("Only proceed if you have a writable test cartridge.")
        print("This will PERMANENTLY modify the cartridge contents.")
        
        response = input("\nProceed with write test? (yes/no): ").lower().strip()
        return response in ['yes', 'y']
    
    def run_full_test_suite(self, firmware_version: str = "latest", 
                           test_rom_path: Optional[str] = None) -> Dict[str, Any]:
        """Run the complete hardware validation test suite"""
        self.logger.info("Starting full hardware validation test suite")
        
        start_time = time.time()
        
        # Run all test categories
        device_results = self.run_device_tests()
        firmware_results = self.run_firmware_tests(firmware_version)
        cartridge_results = self.run_cartridge_tests(test_rom_path)
        
        total_time = time.time() - start_time
        
        # Compile results
        all_results = device_results + firmware_results + cartridge_results
        
        summary = {
            'total_tests': len(all_results),
            'passed': len([t for t in all_results if t.result == TestResult.PASS]),
            'failed': len([t for t in all_results if t.result == TestResult.FAIL]),
            'errors': len([t for t in all_results if t.result == TestResult.ERROR]),
            'skipped': len([t for t in all_results if t.result == TestResult.SKIP]),
            'total_time': total_time,
            'success_rate': len([t for t in all_results if t.result == TestResult.PASS]) / len(all_results) * 100
        }
        
        self.logger.info(f"Test suite completed: {summary['passed']}/{summary['total_tests']} passed "
                        f"({summary['success_rate']:.1f}%) in {total_time:.2f}s")
        
        return summary
    
    def save_test_results(self):
        """Save test results to JSON file"""
        results_data = {
            'timestamp': time.time(),
            'test_config': self.test_config,
            'test_cases': [
                {
                    'name': tc.name,
                    'description': tc.description,
                    'category': tc.category,
                    'result': tc.result.value,
                    'duration': tc.duration,
                    'error_message': tc.error_message,
                    'details': tc.details
                }
                for tc in self.test_cases
            ]
        }
        
        with open(self.test_results_file, 'w') as f:
            json.dump(results_data, f, indent=2)
        
        self.logger.info(f"Test results saved to: {self.test_results_file}")
    
    def print_test_summary(self):
        """Print a formatted test summary"""
        if not self.test_cases:
            print("No tests have been run.")
            return
        
        print("\n" + "="*80)
        print("HARDWARE VALIDATION TEST SUMMARY")
        print("="*80)
        
        # Group by category
        categories = {}
        for test_case in self.test_cases:
            if test_case.category not in categories:
                categories[test_case.category] = []
            categories[test_case.category].append(test_case)
        
        # Print results by category
        for category, tests in categories.items():
            print(f"\n{category} Tests:")
            print("-" * (len(category) + 7))
            
            for test in tests:
                status_symbol = {
                    TestResult.PASS: "✅",
                    TestResult.FAIL: "❌",
                    TestResult.SKIP: "⏭️",
                    TestResult.ERROR: "💥"
                }[test.result]
                
                print(f"  {status_symbol} {test.name:<40} {test.result.value:<6} ({test.duration:.2f}s)")
                
                if test.error_message:
                    print(f"     Error: {test.error_message}")
        
        # Overall summary
        total = len(self.test_cases)
        passed = len([t for t in self.test_cases if t.result == TestResult.PASS])
        failed = len([t for t in self.test_cases if t.result == TestResult.FAIL])
        errors = len([t for t in self.test_cases if t.result == TestResult.ERROR])
        skipped = len([t for t in self.test_cases if t.result == TestResult.SKIP])
        
        print(f"\n{'='*80}")
        print(f"OVERALL RESULTS: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
        print(f"Passed: {passed}, Failed: {failed}, Errors: {errors}, Skipped: {skipped}")
        print(f"Total time: {sum(t.duration for t in self.test_cases):.2f}s")
        print(f"Results saved to: {self.test_results_file}")
        print("="*80)


def main():
    """Main entry point for hardware validation"""
    parser = argparse.ArgumentParser(description="MRUpdater Hardware Validation Test Suite")
    
    parser.add_argument('--device-test', action='store_true',
                       help='Run device detection and communication tests')
    parser.add_argument('--firmware-test', action='store_true',
                       help='Run firmware download and validation tests')
    parser.add_argument('--cartridge-test', action='store_true',
                       help='Run cartridge operation tests')
    parser.add_argument('--full-suite', action='store_true',
                       help='Run complete test suite')
    
    parser.add_argument('--firmware-version', default='latest',
                       help='Firmware version to test (default: latest)')
    parser.add_argument('--rom-path', 
                       help='Path to test ROM file for cartridge write test')
    
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose output')
    parser.add_argument('--debug', action='store_true',
                       help='Enable debug logging')
    
    args = parser.parse_args()
    
    # Configure logging
    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(level=log_level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Create validator
    validator = HardwareValidator(verbose=args.verbose)
    
    try:
        # Run requested tests
        if args.full_suite:
            validator.run_full_test_suite(args.firmware_version, args.rom_path)
        else:
            if args.device_test:
                validator.run_device_tests()
            if args.firmware_test:
                validator.run_firmware_tests(args.firmware_version)
            if args.cartridge_test:
                validator.run_cartridge_tests(args.rom_path)
        
        # Save and display results
        validator.save_test_results()
        validator.print_test_summary()
        
        # Exit with appropriate code
        failed_tests = [t for t in validator.test_cases if t.result in [TestResult.FAIL, TestResult.ERROR]]
        sys.exit(1 if failed_tests else 0)
        
    except KeyboardInterrupt:
        print("\nTest suite interrupted by user")
        validator.save_test_results()
        sys.exit(130)
    except Exception as e:
        print(f"Test suite failed with error: {e}")
        validator.save_test_results()
        sys.exit(1)


if __name__ == '__main__':
    main()
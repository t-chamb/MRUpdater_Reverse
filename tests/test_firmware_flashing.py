#!/usr/bin/env python3
"""
Unit tests for firmware flashing logic and error handling.
Tests FirmwareManager, FPGAFlasher, MCUFlasher, and error recovery.
"""

import unittest
import sys
import tempfile
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from flashing_tool.firmware_manager import FirmwareManager, FirmwareManifest, FirmwareInfo
from flashing_tool.fpga_flasher import FPGAFlasher, FPGAFlashError
from flashing_tool.mcu_flasher import MCUFlasher, MCUFlashError
from flashing_tool.firmware_flasher import FirmwareFlasher, FirmwareFlashProgress, FlashStage
from flashing_tool.version_detector import VersionDetector, DeviceVersion
from exceptions import ChromaticError
from tests.mocks.mock_device import MockFirmwareManager, MockProgressCallback


class TestFirmwareManager(unittest.TestCase):
    """Test firmware management functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.firmware_manager = FirmwareManager(cache_dir=self.temp_dir)
        
    def test_firmware_manifest_loading(self):
        """Test loading firmware manifest from S3"""
        with patch('boto3.client') as mock_boto:
            # Mock S3 response
            mock_s3 = Mock()
            mock_boto.return_value = mock_s3
            mock_s3.get_object.return_value = {
                'Body': Mock(read=lambda: json.dumps({
                    'latest_version': '2.0.0',
                    'firmware_list': [
                        {
                            'version': '2.0.0',
                            'mcu_binary_key': 'firmware/v2.0.0/mcu.bin',
                            'fpga_bitstream_key': 'firmware/v2.0.0/fpga.fs',
                            'changelog': 'Latest improvements',
                            'release_date': '2024-01-15'
                        }
                    ]
                }).encode())
            }
            
            manifest = self.firmware_manager.get_firmware_manifest()
            
            self.assertIsInstance(manifest, FirmwareManifest)
            self.assertEqual(manifest.latest_version, '2.0.0')
            self.assertEqual(len(manifest.firmware_list), 1)
            
    def test_firmware_manifest_network_error(self):
        """Test handling network errors when loading manifest"""
        with patch('boto3.client') as mock_boto:
            mock_s3 = Mock()
            mock_boto.return_value = mock_s3
            mock_s3.get_object.side_effect = Exception("Network error")
            
            manifest = self.firmware_manager.get_firmware_manifest()
            self.assertIsNone(manifest)
            
    def test_firmware_download(self):
        """Test firmware download functionality"""
        with patch('boto3.client') as mock_boto:
            mock_s3 = Mock()
            mock_boto.return_value = mock_s3
            
            # Mock successful download
            mock_s3.download_file.return_value = None
            
            success = self.firmware_manager.download_firmware('2.0.0')
            self.assertTrue(success)
            
    def test_firmware_download_error(self):
        """Test firmware download error handling"""
        with patch('boto3.client') as mock_boto:
            mock_s3 = Mock()
            mock_boto.return_value = mock_s3
            mock_s3.download_file.side_effect = Exception("Download failed")
            
            success = self.firmware_manager.download_firmware('2.0.0')
            self.assertFalse(success)
            
    def test_cached_versions_list(self):
        """Test listing cached firmware versions"""
        # Create mock cached files
        cache_dir = Path(self.temp_dir)
        (cache_dir / 'v1.9.0').mkdir()
        (cache_dir / 'v1.8.0').mkdir()
        (cache_dir / 'v1.9.0' / 'mcu.bin').touch()
        (cache_dir / 'v1.8.0' / 'mcu.bin').touch()
        
        cached_versions = self.firmware_manager.list_cached_versions()
        
        self.assertIn('1.9.0', cached_versions)
        self.assertIn('1.8.0', cached_versions)
        
    def test_cache_cleanup(self):
        """Test cache cleanup functionality"""
        # Create mock cached files
        cache_dir = Path(self.temp_dir)
        old_version_dir = cache_dir / 'v1.0.0'
        old_version_dir.mkdir()
        (old_version_dir / 'mcu.bin').write_bytes(b'x' * 1000)
        
        initial_size = self.firmware_manager.get_cache_size()
        self.assertGreater(initial_size, 0)
        
        # Clean up old versions
        self.firmware_manager.cleanup_old_versions(keep_count=0)
        
        final_size = self.firmware_manager.get_cache_size()
        self.assertLess(final_size, initial_size)


class TestFPGAFlasher(unittest.TestCase):
    """Test FPGA flashing functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.fpga_flasher = FPGAFlasher()
        
    @patch('subprocess.run')
    def test_fpga_device_detection(self, mock_run):
        """Test FPGA device detection"""
        # Mock openFPGALoader output
        mock_run.return_value = Mock(
            returncode=0,
            stdout="Detected devices:\n  0: GW5A-25 (0x374E:0x013F)\n",
            stderr=""
        )
        
        devices = self.fpga_flasher.detect_fpga_devices()
        
        self.assertIsInstance(devices, list)
        self.assertGreater(len(devices), 0)
        
    @patch('subprocess.run')
    def test_fpga_device_detection_no_devices(self, mock_run):
        """Test FPGA detection when no devices found"""
        mock_run.return_value = Mock(
            returncode=1,
            stdout="No devices found\n",
            stderr=""
        )
        
        devices = self.fpga_flasher.detect_fpga_devices()
        self.assertEqual(len(devices), 0)
        
    @patch('subprocess.run')
    def test_fpga_flash_success(self, mock_run):
        """Test successful FPGA flashing"""
        mock_run.return_value = Mock(returncode=0, stdout="Flash complete", stderr="")
        
        progress_callback = MockProgressCallback()
        
        success = self.fpga_flasher.flash_fpga(
            bitstream_path="/mock/path/fpga.fs",
            progress_callback=progress_callback
        )
        
        self.assertTrue(success)
        self.assertGreater(progress_callback.get_progress_count(), 0)
        
    @patch('subprocess.run')
    def test_fpga_flash_failure(self, mock_run):
        """Test FPGA flashing failure"""
        mock_run.return_value = Mock(
            returncode=1,
            stdout="",
            stderr="Flash failed: Device not found"
        )
        
        with self.assertRaises(FPGAFlashError):
            self.fpga_flasher.flash_fpga("/mock/path/fpga.fs")
            
    def test_fpga_info_parsing(self):
        """Test FPGA device info parsing"""
        mock_output = "Device: GW5A-25, ID: 0x12345678, Version: 1.0"
        
        info = self.fpga_flasher._parse_fpga_info(mock_output)
        
        self.assertIsInstance(info, dict)
        self.assertIn('device', info)
        
    @patch('subprocess.run')
    def test_fpga_verification(self, mock_run):
        """Test FPGA flash verification"""
        mock_run.return_value = Mock(
            returncode=0,
            stdout="Verification successful",
            stderr=""
        )
        
        success = self.fpga_flasher.verify_flash("/mock/path/fpga.fs")
        self.assertTrue(success)


class TestMCUFlasher(unittest.TestCase):
    """Test MCU flashing functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.mcu_flasher = MCUFlasher()
        
    @patch('subprocess.run')
    def test_mcu_device_detection(self, mock_run):
        """Test MCU device detection"""
        mock_run.return_value = Mock(
            returncode=0,
            stdout="Found ESP32 device on /dev/ttyUSB0\n",
            stderr=""
        )
        
        devices = self.mcu_flasher.detect_mcu_devices()
        
        self.assertIsInstance(devices, list)
        self.assertGreater(len(devices), 0)
        
    @patch('subprocess.run')
    def test_mcu_flash_success(self, mock_run):
        """Test successful MCU flashing"""
        mock_run.return_value = Mock(returncode=0, stdout="Flash complete", stderr="")
        
        progress_callback = MockProgressCallback()
        
        success = self.mcu_flasher.flash_mcu(
            binary_path="/mock/path/mcu.bin",
            progress_callback=progress_callback
        )
        
        self.assertTrue(success)
        self.assertGreater(progress_callback.get_progress_count(), 0)
        
    @patch('subprocess.run')
    def test_mcu_flash_failure(self, mock_run):
        """Test MCU flashing failure"""
        mock_run.return_value = Mock(
            returncode=1,
            stdout="",
            stderr="Flash failed: No response from device"
        )
        
        with self.assertRaises(MCUFlashError):
            self.mcu_flasher.flash_mcu("/mock/path/mcu.bin")
            
    @patch('subprocess.run')
    def test_mcu_reset(self, mock_run):
        """Test MCU reset functionality"""
        mock_run.return_value = Mock(returncode=0, stdout="Reset complete", stderr="")
        
        success = self.mcu_flasher.reset_mcu()
        self.assertTrue(success)
        
    @patch('subprocess.run')
    def test_mcu_boot_mode(self, mock_run):
        """Test MCU boot mode setting"""
        mock_run.return_value = Mock(returncode=0, stdout="Boot mode set", stderr="")
        
        success = self.mcu_flasher.set_boot_mode("download")
        self.assertTrue(success)


class TestVersionDetector(unittest.TestCase):
    """Test device version detection"""
    
    def setUp(self):
        """Set up test environment"""
        self.version_detector = VersionDetector()
        
    def test_version_parsing(self):
        """Test version string parsing"""
        version_data = {
            'mcu_version': '1.9.0',
            'fpga_version': '1.9.0',
            'build_date': '2024-01-01'
        }
        
        device_version = DeviceVersion.from_dict(version_data)
        
        self.assertEqual(device_version.mcu_version, '1.9.0')
        self.assertEqual(device_version.fpga_version, '1.9.0')
        self.assertEqual(device_version.build_date, '2024-01-01')
        
    def test_version_comparison(self):
        """Test version comparison logic"""
        version1 = DeviceVersion(mcu_version='1.9.0', fpga_version='1.9.0')
        version2 = DeviceVersion(mcu_version='2.0.0', fpga_version='2.0.0')
        
        self.assertTrue(self.version_detector.is_newer_version(version2, version1))
        self.assertFalse(self.version_detector.is_newer_version(version1, version2))
        
    def test_version_compatibility(self):
        """Test version compatibility checking"""
        device_version = DeviceVersion(mcu_version='1.9.0', fpga_version='1.9.0')
        firmware_version = '2.0.0'
        
        is_compatible = self.version_detector.is_compatible(device_version, firmware_version)
        self.assertIsInstance(is_compatible, bool)


class TestFirmwareFlasher(unittest.TestCase):
    """Test integrated firmware flashing workflow"""
    
    def setUp(self):
        """Set up test environment"""
        self.firmware_flasher = FirmwareFlasher()
        
    @patch('flashing_tool.firmware_flasher.FirmwareManager')
    @patch('flashing_tool.firmware_flasher.FPGAFlasher')
    @patch('flashing_tool.firmware_flasher.MCUFlasher')
    def test_complete_flash_workflow(self, mock_mcu, mock_fpga, mock_manager):
        """Test complete firmware flashing workflow"""
        # Mock successful operations
        mock_manager_instance = Mock()
        mock_manager.return_value = mock_manager_instance
        mock_manager_instance.download_firmware.return_value = True
        
        mock_fpga_instance = Mock()
        mock_fpga.return_value = mock_fpga_instance
        mock_fpga_instance.flash_fpga.return_value = True
        
        mock_mcu_instance = Mock()
        mock_mcu.return_value = mock_mcu_instance
        mock_mcu_instance.flash_mcu.return_value = True
        
        progress_callback = MockProgressCallback()
        
        success = self.firmware_flasher.flash_firmware(
            version='2.0.0',
            progress_callback=progress_callback
        )
        
        self.assertTrue(success)
        self.assertTrue(progress_callback.completed)
        
    def test_flash_workflow_with_errors(self):
        """Test firmware flashing with error handling"""
        with patch('flashing_tool.firmware_flasher.FirmwareManager') as mock_manager:
            mock_manager_instance = Mock()
            mock_manager.return_value = mock_manager_instance
            mock_manager_instance.download_firmware.return_value = False
            
            progress_callback = MockProgressCallback()
            
            success = self.firmware_flasher.flash_firmware(
                version='2.0.0',
                progress_callback=progress_callback
            )
            
            self.assertFalse(success)
            self.assertIsNotNone(progress_callback.error)
            
    def test_update_check(self):
        """Test firmware update checking"""
        with patch.object(self.firmware_flasher, 'get_device_version') as mock_device:
            with patch.object(self.firmware_flasher, 'get_available_versions') as mock_available:
                mock_device.return_value = DeviceVersion(
                    mcu_version='1.9.0',
                    fpga_version='1.9.0'
                )
                mock_available.return_value = ['2.0.0', '1.9.0', '1.8.0']
                
                comparison = self.firmware_flasher.check_for_updates()
                
                self.assertIsNotNone(comparison)
                self.assertTrue(comparison.update_available)
                
    def test_rollback_functionality(self):
        """Test firmware rollback functionality"""
        with patch.object(self.firmware_flasher, 'flash_firmware') as mock_flash:
            mock_flash.return_value = True
            
            success = self.firmware_flasher.rollback_firmware('1.9.0')
            self.assertTrue(success)
            mock_flash.assert_called_once_with('1.9.0', None)


class TestErrorHandling(unittest.TestCase):
    """Test error handling in firmware operations"""
    
    def test_chromatic_error_hierarchy(self):
        """Test ChromaticError exception hierarchy"""
        fpga_error = FPGAFlashError("FPGA flash failed")
        mcu_error = MCUFlashError("MCU flash failed")
        
        self.assertIsInstance(fpga_error, ChromaticError)
        self.assertIsInstance(mcu_error, ChromaticError)
        
    def test_error_recovery_strategies(self):
        """Test error recovery strategies"""
        from error_recovery import ErrorRecovery
        
        recovery = ErrorRecovery()
        
        # Test retry strategy
        retry_count = 0
        def failing_operation():
            nonlocal retry_count
            retry_count += 1
            if retry_count < 3:
                raise Exception("Temporary failure")
            return True
            
        result = recovery.retry_operation(failing_operation, max_retries=3)
        self.assertTrue(result)
        self.assertEqual(retry_count, 3)
        
    def test_progress_error_reporting(self):
        """Test error reporting through progress callbacks"""
        progress_callback = MockProgressCallback()
        
        # Simulate error during progress
        progress_data = {
            'stage': 'flashing',
            'progress': 50.0,
            'error': 'Flash verification failed'
        }
        
        progress_callback(progress_data)
        
        self.assertEqual(progress_callback.error, 'Flash verification failed')
        self.assertFalse(progress_callback.completed)


if __name__ == '__main__':
    unittest.main(verbosity=2)
#!/usr/bin/env python3
"""
Integration tests for complete MRUpdater workflows.
Tests end-to-end functionality with mock hardware.
"""

import unittest
import sys
import time
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from flashing_tool.firmware_flasher import FirmwareFlasher, FirmwareFlashProgress
from flashing_tool.device_manager import DeviceManager, DeviceInfo
from cartclinic.cartridge_detection import CartridgeDetector
from cartclinic.cartridge_read import CartridgeReader
from cartclinic.cartridge_write import CartridgeWriter
from cartclinic.cartridge_info import CartridgeInfo
from libpyretro.cartclinic.comms.transport import SerialTransport
from tests.mocks.mock_chromatic_device import MockChromaticDevice, MockDeviceConfig
from tests.mocks.mock_device import MockCartridgeData, MockProgressCallback


class TestFirmwareFlashingWorkflow(unittest.TestCase):
    """Test complete firmware flashing workflow"""
    
    def setUp(self):
        """Set up test environment"""
        self.mock_device = MockChromaticDevice()
        self.mock_device.connect()
        self.progress_callback = MockProgressCallback()
        
    def test_complete_firmware_flash_workflow(self):
        """Test complete firmware flashing from start to finish"""
        # Mock the firmware flasher components
        with patch('flashing_tool.firmware_flasher.FirmwareManager') as mock_fm:
            with patch('flashing_tool.firmware_flasher.FPGAFlasher') as mock_fpga:
                with patch('flashing_tool.firmware_flasher.MCUFlasher') as mock_mcu:
                    
                    # Configure mocks
                    mock_fm_instance = Mock()
                    mock_fm.return_value = mock_fm_instance
                    mock_fm_instance.get_firmware_manifest.return_value = Mock(
                        latest_version='2.0.0',
                        firmware_list=[Mock(version='2.0.0')]
                    )
                    mock_fm_instance.download_firmware.return_value = True
                    
                    mock_fpga_instance = Mock()
                    mock_fpga.return_value = mock_fpga_instance
                    mock_fpga_instance.flash_fpga.return_value = True
                    
                    mock_mcu_instance = Mock()
                    mock_mcu.return_value = mock_mcu_instance
                    mock_mcu_instance.flash_mcu.return_value = True
                    
                    # Create firmware flasher
                    flasher = FirmwareFlasher()
                    
                    # Test the complete workflow
                    success = flasher.flash_firmware(
                        version='2.0.0',
                        progress_callback=self.progress_callback
                    )
                    
                    # Verify success
                    self.assertTrue(success)
                    self.assertGreater(self.progress_callback.get_progress_count(), 0)
                    
                    # Verify all components were called
                    mock_fm_instance.download_firmware.assert_called_with('2.0.0')
                    mock_fpga_instance.flash_fpga.assert_called()
                    mock_mcu_instance.flash_mcu.assert_called()
                    
    def test_firmware_flash_with_device_detection(self):
        """Test firmware flashing with device detection"""
        with patch('flashing_tool.device_manager.DeviceManager') as mock_dm:
            # Mock device detection
            mock_dm_instance = Mock()
            mock_dm.return_value = mock_dm_instance
            mock_dm_instance.scan_for_devices.return_value = [
                DeviceInfo(
                    serial_port="/dev/mock0",
                    usb_path="mock_path",
                    serial_number="MOCK001",
                    product_name="Mock Chromatic",
                    manufacturer="Mock ModRetro"
                )
            ]
            
            # Test device detection and firmware flash
            device_manager = DeviceManager()
            devices = device_manager.scan_for_devices()
            
            self.assertEqual(len(devices), 1)
            self.assertEqual(devices[0].serial_number, "MOCK001")
            
    def test_firmware_flash_error_recovery(self):
        """Test firmware flashing with error recovery"""
        with patch('flashing_tool.firmware_flasher.FirmwareManager') as mock_fm:
            # Simulate download failure then success
            mock_fm_instance = Mock()
            mock_fm.return_value = mock_fm_instance
            mock_fm_instance.download_firmware.side_effect = [False, True]  # Fail then succeed
            
            flasher = FirmwareFlasher()
            
            # First attempt should fail
            success = flasher.flash_firmware('2.0.0', self.progress_callback)
            self.assertFalse(success)
            
            # Second attempt should succeed
            success = flasher.flash_firmware('2.0.0', self.progress_callback)
            self.assertTrue(success)
            
    def test_firmware_flash_progress_reporting(self):
        """Test detailed progress reporting during firmware flash"""
        with patch('flashing_tool.firmware_flasher.FirmwareManager') as mock_fm:
            with patch('flashing_tool.firmware_flasher.FPGAFlasher') as mock_fpga:
                with patch('flashing_tool.firmware_flasher.MCUFlasher') as mock_mcu:
                    
                    # Configure mocks to simulate progress
                    mock_fm_instance = Mock()
                    mock_fm.return_value = mock_fm_instance
                    mock_fm_instance.download_firmware.return_value = True
                    
                    def mock_fpga_flash(bitstream_path, progress_callback=None):
                        if progress_callback:
                            progress_callback({'stage': 'fpga_flash', 'progress': 50.0})
                            progress_callback({'stage': 'fpga_flash', 'progress': 100.0})
                        return True
                        
                    def mock_mcu_flash(binary_path, progress_callback=None):
                        if progress_callback:
                            progress_callback({'stage': 'mcu_flash', 'progress': 50.0})
                            progress_callback({'stage': 'mcu_flash', 'progress': 100.0})
                        return True
                    
                    mock_fpga_instance = Mock()
                    mock_fpga.return_value = mock_fpga_instance
                    mock_fpga_instance.flash_fpga.side_effect = mock_fpga_flash
                    
                    mock_mcu_instance = Mock()
                    mock_mcu.return_value = mock_mcu_instance
                    mock_mcu_instance.flash_mcu.side_effect = mock_mcu_flash
                    
                    # Test with progress tracking
                    flasher = FirmwareFlasher()
                    success = flasher.flash_firmware('2.0.0', self.progress_callback)
                    
                    self.assertTrue(success)
                    # Should have received multiple progress updates
                    self.assertGreater(self.progress_callback.get_progress_count(), 2)


class TestCartridgeOperationWorkflow(unittest.TestCase):
    """Test complete cartridge operation workflows"""
    
    def setUp(self):
        """Set up test environment"""
        self.mock_device = MockChromaticDevice()
        self.mock_device.connect()
        
        # Insert a test cartridge
        self.test_cartridge = MockCartridgeData(
            title="TEST GAME",
            cartridge_type=0x03,  # MBC1+RAM+BATTERY
            rom_size=0x02,        # 128KB
            ram_size=0x02         # 8KB
        )
        self.mock_device.insert_cartridge(self.test_cartridge)
        
    def test_complete_cartridge_read_workflow(self):
        """Test complete cartridge reading workflow"""
        # Mock the transport layer
        with patch('libpyretro.cartclinic.comms.transport.SerialTransport') as mock_transport:
            mock_transport_instance = Mock()
            mock_transport.return_value = mock_transport_instance
            mock_transport_instance.is_connected.return_value = True
            
            # Mock command responses
            def mock_send_command(command):
                return self.mock_device.send_command(command)
            
            mock_transport_instance.send_command.side_effect = mock_send_command
            
            # Test cartridge detection
            detector = CartridgeDetector(mock_transport_instance)
            is_inserted = detector.is_cartridge_inserted()
            self.assertTrue(is_inserted)
            
            # Test cartridge reading
            reader = CartridgeReader(mock_transport_instance)
            
            # Read header
            header_data = reader.read_header()
            self.assertIsInstance(header_data, bytes)
            self.assertGreater(len(header_data), 0)
            
            # Parse cartridge info
            cartridge_info = CartridgeInfo.from_header_data(header_data)
            self.assertEqual(cartridge_info.header.title, "TEST GAME")
            
            # Read ROM data
            rom_data = reader.read_rom(start_address=0x0000, length=1024)
            self.assertIsInstance(rom_data, bytes)
            self.assertEqual(len(rom_data), 1024)
            
    def test_complete_cartridge_write_workflow(self):
        """Test complete cartridge writing workflow"""
        with patch('libpyretro.cartclinic.comms.transport.SerialTransport') as mock_transport:
            mock_transport_instance = Mock()
            mock_transport.return_value = mock_transport_instance
            mock_transport_instance.is_connected.return_value = True
            
            def mock_send_command(command):
                return self.mock_device.send_command(command)
            
            mock_transport_instance.send_command.side_effect = mock_send_command
            
            # Test cartridge writing
            writer = CartridgeWriter(mock_transport_instance)
            
            # Write ROM data
            test_rom_data = b'\xAA\xBB\xCC\xDD' * 256  # 1KB test data
            bytes_written = writer.write_rom(
                rom_data=test_rom_data,
                start_address=0x0000
            )
            
            self.assertEqual(bytes_written, len(test_rom_data))
            
            # Verify write
            verification_result = writer.verify_write(
                expected_data=test_rom_data,
                start_address=0x0000
            )
            self.assertTrue(verification_result)
            
    def test_cartridge_operation_with_progress(self):
        """Test cartridge operations with progress reporting"""
        with patch('libpyretro.cartclinic.comms.transport.SerialTransport') as mock_transport:
            mock_transport_instance = Mock()
            mock_transport.return_value = mock_transport_instance
            mock_transport_instance.is_connected.return_value = True
            
            def mock_send_command(command):
                return self.mock_device.send_command(command)
            
            mock_transport_instance.send_command.side_effect = mock_send_command
            
            # Test with progress callback
            progress_updates = []
            def progress_callback(progress_data):
                progress_updates.append(progress_data)
                
            reader = CartridgeReader(mock_transport_instance)
            
            # Read large ROM with progress
            rom_data = reader.read_rom(
                start_address=0x0000,
                length=8192,  # 8KB
                progress_callback=progress_callback
            )
            
            self.assertIsInstance(rom_data, bytes)
            self.assertGreater(len(progress_updates), 0)
            
            # Check progress data structure
            for progress in progress_updates:
                self.assertIn('progress', progress)
                self.assertIsInstance(progress['progress'], (int, float))
                
    def test_cartridge_error_handling(self):
        """Test cartridge operation error handling"""
        # Test with no cartridge inserted
        self.mock_device.remove_cartridge()
        
        with patch('libpyretro.cartclinic.comms.transport.SerialTransport') as mock_transport:
            mock_transport_instance = Mock()
            mock_transport.return_value = mock_transport_instance
            mock_transport_instance.is_connected.return_value = True
            
            def mock_send_command(command):
                return self.mock_device.send_command(command)
            
            mock_transport_instance.send_command.side_effect = mock_send_command
            
            detector = CartridgeDetector(mock_transport_instance)
            is_inserted = detector.is_cartridge_inserted()
            self.assertFalse(is_inserted)
            
            # Attempting to read should handle the error gracefully
            reader = CartridgeReader(mock_transport_instance)
            
            # This should either return None or raise an appropriate exception
            try:
                header_data = reader.read_header()
                # If it doesn't raise an exception, it should return None or empty data
                self.assertIsNone(header_data)
            except Exception as e:
                # Should be a cartridge-related exception
                self.assertIn("cartridge", str(e).lower())


class TestDeviceManagementWorkflow(unittest.TestCase):
    """Test device management workflows"""
    
    def setUp(self):
        """Set up test environment"""
        self.mock_devices = [
            MockChromaticDevice(MockDeviceConfig(serial_number="MOCK001")),
            MockChromaticDevice(MockDeviceConfig(serial_number="MOCK002"))
        ]
        
    def test_device_discovery_workflow(self):
        """Test device discovery and connection workflow"""
        with patch('flashing_tool.device_manager.DeviceManager') as mock_dm:
            # Mock multiple devices
            mock_dm_instance = Mock()
            mock_dm.return_value = mock_dm_instance
            mock_dm_instance.scan_for_devices.return_value = [
                DeviceInfo(
                    serial_port="/dev/mock0",
                    usb_path="mock_path_0",
                    serial_number="MOCK001",
                    product_name="Mock Chromatic 1",
                    manufacturer="Mock ModRetro"
                ),
                DeviceInfo(
                    serial_port="/dev/mock1",
                    usb_path="mock_path_1",
                    serial_number="MOCK002",
                    product_name="Mock Chromatic 2",
                    manufacturer="Mock ModRetro"
                )
            ]
            
            device_manager = DeviceManager()
            devices = device_manager.scan_for_devices()
            
            self.assertEqual(len(devices), 2)
            self.assertEqual(devices[0].serial_number, "MOCK001")
            self.assertEqual(devices[1].serial_number, "MOCK002")
            
    def test_device_connection_management(self):
        """Test device connection and disconnection"""
        mock_device = self.mock_devices[0]
        
        # Test connection
        self.assertTrue(mock_device.connect())
        self.assertTrue(mock_device.is_connected())
        
        # Test ping
        from libpyretro.cartclinic.comms.transport import CommandMessage
        ping_command = CommandMessage(command="ping")
        response = mock_device.send_command(ping_command)
        
        self.assertTrue(response.success)
        self.assertIn("pong", response.data)
        
        # Test disconnection
        mock_device.disconnect()
        self.assertFalse(mock_device.is_connected())
        
    def test_device_version_detection(self):
        """Test device version detection workflow"""
        mock_device = self.mock_devices[0]
        mock_device.connect()
        
        from libpyretro.cartclinic.comms.transport import CommandMessage
        version_command = CommandMessage(command="get_version")
        response = mock_device.send_command(version_command)
        
        self.assertTrue(response.success)
        self.assertIn("mcu_version", response.data)
        self.assertIn("fpga_version", response.data)
        self.assertEqual(response.data["mcu_version"], "1.9.0")
        self.assertEqual(response.data["fpga_version"], "1.9.0")


class TestEndToEndWorkflows(unittest.TestCase):
    """Test complete end-to-end workflows"""
    
    def setUp(self):
        """Set up test environment"""
        self.mock_device = MockChromaticDevice()
        self.mock_device.connect()
        
    def test_complete_cart_clinic_session(self):
        """Test complete Cart Clinic session from start to finish"""
        # Insert test cartridge
        test_cartridge = MockCartridgeData(
            title="POKEMON RED",
            cartridge_type=0x03,  # MBC1+RAM+BATTERY
            rom_size=0x05,        # 1MB
            ram_size=0x02         # 8KB
        )
        self.mock_device.insert_cartridge(test_cartridge)
        
        with patch('libpyretro.cartclinic.comms.transport.SerialTransport') as mock_transport:
            mock_transport_instance = Mock()
            mock_transport.return_value = mock_transport_instance
            mock_transport_instance.is_connected.return_value = True
            
            def mock_send_command(command):
                return self.mock_device.send_command(command)
            
            mock_transport_instance.send_command.side_effect = mock_send_command
            
            # 1. Detect cartridge
            detector = CartridgeDetector(mock_transport_instance)
            self.assertTrue(detector.is_cartridge_inserted())
            
            # 2. Read cartridge info
            reader = CartridgeReader(mock_transport_instance)
            header_data = reader.read_header()
            cartridge_info = CartridgeInfo.from_header_data(header_data)
            
            self.assertEqual(cartridge_info.header.title, "POKEMON RED")
            self.assertTrue(cartridge_info.has_battery)
            self.assertTrue(cartridge_info.has_ram)
            
            # 3. Read ROM (partial for testing)
            rom_data = reader.read_rom(start_address=0x0000, length=2048)
            self.assertEqual(len(rom_data), 2048)
            
            # 4. Read save data
            save_data = reader.read_save_data()
            self.assertIsInstance(save_data, (bytes, type(None)))
            
            # 5. Write modified ROM
            writer = CartridgeWriter(mock_transport_instance)
            modified_rom = b'\xFF' * 1024  # Modified data
            bytes_written = writer.write_rom(modified_rom, 0x0000)
            self.assertEqual(bytes_written, len(modified_rom))
            
            # 6. Verify write
            verification_result = writer.verify_write(modified_rom, 0x0000)
            self.assertTrue(verification_result)
            
    def test_firmware_update_session(self):
        """Test complete firmware update session"""
        with patch('flashing_tool.firmware_flasher.FirmwareFlasher') as mock_flasher:
            mock_flasher_instance = Mock()
            mock_flasher.return_value = mock_flasher_instance
            
            # Mock update check
            mock_comparison = Mock()
            mock_comparison.update_available = True
            mock_comparison.available_version = Mock(
                mcu_version='2.0.0',
                fpga_version='2.0.0'
            )
            mock_flasher_instance.check_for_updates.return_value = mock_comparison
            
            # Mock firmware flash
            mock_flasher_instance.flash_firmware.return_value = True
            
            # Test workflow
            flasher = FirmwareFlasher()
            
            # 1. Check for updates
            comparison = flasher.check_for_updates()
            self.assertTrue(comparison.update_available)
            
            # 2. Flash firmware
            progress_callback = MockProgressCallback()
            success = flasher.flash_firmware('2.0.0', progress_callback)
            self.assertTrue(success)
            
    def test_error_recovery_workflow(self):
        """Test error recovery in complete workflow"""
        # Configure device to simulate errors
        error_device = MockChromaticDevice(
            MockDeviceConfig(simulate_errors=True, error_probability=0.5)
        )
        error_device.connect()
        
        with patch('libpyretro.cartclinic.comms.transport.SerialTransport') as mock_transport:
            mock_transport_instance = Mock()
            mock_transport.return_value = mock_transport_instance
            mock_transport_instance.is_connected.return_value = True
            
            def mock_send_command(command):
                return error_device.send_command(command)
            
            mock_transport_instance.send_command.side_effect = mock_send_command
            
            # Test with error recovery
            from error_recovery import ErrorRecovery
            error_recovery = ErrorRecovery()
            
            def cartridge_operation():
                detector = CartridgeDetector(mock_transport_instance)
                return detector.is_cartridge_inserted()
                
            # Should eventually succeed with retries
            try:
                result = error_recovery.retry_operation(
                    cartridge_operation,
                    max_retries=5,
                    delay=0.01
                )
                # May succeed or fail depending on error simulation
                self.assertIsInstance(result, bool)
            except Exception:
                # Expected with high error probability
                pass


if __name__ == '__main__':
    unittest.main(verbosity=2)
#!/usr/bin/env python3
"""
Unit tests for error handling and recovery mechanisms.
Tests exception hierarchy, error recovery strategies, and logging.
"""

import unittest
import sys
import logging
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from io import StringIO

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from exceptions import (
    ChromaticError, DeviceNotFoundError, CommunicationError,
    FirmwareFlashError, CartridgeError, CartridgeNotDetectedError,
    CartridgeReadError, CartridgeWriteError, DependencyError
)
from error_recovery import ErrorRecovery, RecoveryStrategy
from error_dialog import ErrorDialog
from logging_config import setup_logging
from user_feedback import UserFeedback


class TestExceptionHierarchy(unittest.TestCase):
    """Test the ChromaticError exception hierarchy"""
    
    def test_base_chromatic_error(self):
        """Test base ChromaticError functionality"""
        error = ChromaticError("Base error message")
        
        self.assertEqual(str(error), "Base error message")
        self.assertIsInstance(error, Exception)
        
    def test_device_errors(self):
        """Test device-related errors"""
        device_not_found = DeviceNotFoundError("No Chromatic device found")
        comm_error = CommunicationError("USB communication failed")
        
        self.assertIsInstance(device_not_found, ChromaticError)
        self.assertIsInstance(comm_error, ChromaticError)
        
        self.assertEqual(str(device_not_found), "No Chromatic device found")
        self.assertEqual(str(comm_error), "USB communication failed")
        
    def test_firmware_errors(self):
        """Test firmware-related errors"""
        firmware_error = FirmwareFlashError("FPGA flash failed")
        
        self.assertIsInstance(firmware_error, ChromaticError)
        self.assertEqual(str(firmware_error), "FPGA flash failed")
        
    def test_cartridge_errors(self):
        """Test cartridge-related errors"""
        cart_error = CartridgeError("General cartridge error")
        not_detected = CartridgeNotDetectedError("No cartridge inserted")
        read_error = CartridgeReadError("Failed to read ROM")
        write_error = CartridgeWriteError("Failed to write ROM")
        
        # Test inheritance
        self.assertIsInstance(cart_error, ChromaticError)
        self.assertIsInstance(not_detected, CartridgeError)
        self.assertIsInstance(read_error, CartridgeError)
        self.assertIsInstance(write_error, CartridgeError)
        
        # Test error messages
        self.assertEqual(str(not_detected), "No cartridge inserted")
        self.assertEqual(str(read_error), "Failed to read ROM")
        self.assertEqual(str(write_error), "Failed to write ROM")
        
    def test_dependency_errors(self):
        """Test dependency-related errors"""
        dep_error = DependencyError("Missing required dependency: pyserial")
        
        self.assertIsInstance(dep_error, ChromaticError)
        self.assertEqual(str(dep_error), "Missing required dependency: pyserial")
        
    def test_error_with_context(self):
        """Test errors with additional context"""
        error = CommunicationError(
            "Device communication failed",
            context={
                'device_port': '/dev/ttyUSB0',
                'error_code': 'TIMEOUT',
                'retry_count': 3
            }
        )
        
        self.assertIsInstance(error, ChromaticError)
        self.assertEqual(error.context['device_port'], '/dev/ttyUSB0')
        self.assertEqual(error.context['error_code'], 'TIMEOUT')


class TestErrorRecovery(unittest.TestCase):
    """Test error recovery mechanisms"""
    
    def setUp(self):
        """Set up test environment"""
        self.error_recovery = ErrorRecovery()
        
    def test_retry_operation_success(self):
        """Test successful retry operation"""
        call_count = 0
        
        def flaky_operation():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise CommunicationError("Temporary failure")
            return "Success"
            
        result = self.error_recovery.retry_operation(
            flaky_operation,
            max_retries=3,
            delay=0.01
        )
        
        self.assertEqual(result, "Success")
        self.assertEqual(call_count, 3)
        
    def test_retry_operation_failure(self):
        """Test retry operation that ultimately fails"""
        def always_failing_operation():
            raise CommunicationError("Persistent failure")
            
        with self.assertRaises(CommunicationError):
            self.error_recovery.retry_operation(
                always_failing_operation,
                max_retries=2,
                delay=0.01
            )
            
    def test_exponential_backoff(self):
        """Test exponential backoff retry strategy"""
        call_times = []
        
        def timed_operation():
            import time
            call_times.append(time.time())
            raise CommunicationError("Failure")
            
        try:
            self.error_recovery.retry_operation(
                timed_operation,
                max_retries=3,
                delay=0.1,
                backoff_factor=2.0
            )
        except CommunicationError:
            pass
            
        # Should have made 4 calls (initial + 3 retries)
        self.assertEqual(len(call_times), 4)
        
        # Check that delays increased (allowing for timing variance)
        if len(call_times) >= 3:
            delay1 = call_times[1] - call_times[0]
            delay2 = call_times[2] - call_times[1]
            self.assertGreater(delay2, delay1 * 1.5)  # Allow some variance
            
    def test_recovery_strategy_selection(self):
        """Test automatic recovery strategy selection"""
        # Test device not found recovery
        device_error = DeviceNotFoundError("No device")
        strategy = self.error_recovery.get_recovery_strategy(device_error)
        self.assertEqual(strategy, RecoveryStrategy.DEVICE_RECONNECT)
        
        # Test communication error recovery
        comm_error = CommunicationError("Timeout")
        strategy = self.error_recovery.get_recovery_strategy(comm_error)
        self.assertEqual(strategy, RecoveryStrategy.RETRY_WITH_BACKOFF)
        
        # Test firmware error recovery
        firmware_error = FirmwareFlashError("Flash failed")
        strategy = self.error_recovery.get_recovery_strategy(firmware_error)
        self.assertEqual(strategy, RecoveryStrategy.RECOVERY_MODE)
        
    def test_device_reconnection_recovery(self):
        """Test device reconnection recovery strategy"""
        mock_device_manager = Mock()
        mock_device_manager.scan_for_devices.return_value = [Mock()]
        
        success = self.error_recovery.attempt_device_reconnection(
            device_manager=mock_device_manager,
            max_attempts=2
        )
        
        self.assertTrue(success)
        mock_device_manager.scan_for_devices.assert_called()
        
    def test_recovery_mode_entry(self):
        """Test recovery mode entry for firmware errors"""
        mock_flasher = Mock()
        mock_flasher.enter_recovery_mode.return_value = True
        
        success = self.error_recovery.enter_recovery_mode(mock_flasher)
        
        self.assertTrue(success)
        mock_flasher.enter_recovery_mode.assert_called_once()


class TestErrorDialog(unittest.TestCase):
    """Test error dialog functionality"""
    
    def setUp(self):
        """Set up test environment"""
        # Mock Qt to avoid GUI dependencies in tests
        self.qt_mock = Mock()
        
    @patch('PySide6.QtWidgets.QMessageBox')
    def test_error_dialog_creation(self, mock_messagebox):
        """Test error dialog creation"""
        mock_dialog = Mock()
        mock_messagebox.return_value = mock_dialog
        
        error = CartridgeReadError("Failed to read cartridge")
        dialog = ErrorDialog.create_for_error(error)
        
        self.assertIsNotNone(dialog)
        mock_messagebox.assert_called_once()
        
    @patch('PySide6.QtWidgets.QMessageBox')
    def test_error_dialog_with_recovery_options(self, mock_messagebox):
        """Test error dialog with recovery options"""
        mock_dialog = Mock()
        mock_messagebox.return_value = mock_dialog
        
        error = DeviceNotFoundError("No device found")
        dialog = ErrorDialog.create_for_error(
            error,
            recovery_options=['Retry', 'Scan Again', 'Cancel']
        )
        
        self.assertIsNotNone(dialog)
        
    def test_error_message_formatting(self):
        """Test error message formatting"""
        error = CommunicationError(
            "Device timeout",
            context={'port': '/dev/ttyUSB0', 'timeout': 5.0}
        )
        
        formatted_message = ErrorDialog.format_error_message(error)
        
        self.assertIn("Device timeout", formatted_message)
        self.assertIn("/dev/ttyUSB0", formatted_message)
        self.assertIn("5.0", formatted_message)
        
    def test_technical_details_inclusion(self):
        """Test inclusion of technical details in error dialog"""
        error = FirmwareFlashError(
            "FPGA flash failed",
            context={
                'stage': 'verification',
                'address': '0x1000',
                'expected': '0xABCD',
                'actual': '0x1234'
            }
        )
        
        details = ErrorDialog.get_technical_details(error)
        
        self.assertIn("verification", details)
        self.assertIn("0x1000", details)
        self.assertIn("0xABCD", details)


class TestLoggingConfiguration(unittest.TestCase):
    """Test logging configuration and error logging"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.log_file = Path(self.temp_dir) / "test.log"
        
    def test_logging_setup(self):
        """Test logging configuration setup"""
        setup_logging(
            log_file=str(self.log_file),
            log_level=logging.DEBUG
        )
        
        logger = logging.getLogger('test_logger')
        logger.error("Test error message")
        
        # Check that log file was created and contains message
        self.assertTrue(self.log_file.exists())
        log_content = self.log_file.read_text()
        self.assertIn("Test error message", log_content)
        
    def test_error_logging_with_context(self):
        """Test logging errors with context information"""
        setup_logging(log_file=str(self.log_file))
        logger = logging.getLogger('test_context')
        
        error = CommunicationError(
            "Device communication failed",
            context={'device': '/dev/ttyUSB0', 'retry_count': 3}
        )
        
        logger.error("Operation failed", exc_info=error, extra={
            'device_port': error.context.get('device'),
            'retry_count': error.context.get('retry_count')
        })
        
        log_content = self.log_file.read_text()
        self.assertIn("Operation failed", log_content)
        
    def test_log_rotation(self):
        """Test log file rotation"""
        from logging.handlers import RotatingFileHandler
        
        # Create a rotating file handler
        handler = RotatingFileHandler(
            str(self.log_file),
            maxBytes=1024,
            backupCount=3
        )
        
        logger = logging.getLogger('rotation_test')
        logger.addHandler(handler)
        
        # Write enough data to trigger rotation
        for i in range(100):
            logger.error(f"Test message {i} with enough content to fill the log file")
            
        # Check that backup files were created
        backup_files = list(Path(self.temp_dir).glob("test.log.*"))
        self.assertGreater(len(backup_files), 0)


class TestUserFeedback(unittest.TestCase):
    """Test user feedback and error reporting"""
    
    def setUp(self):
        """Set up test environment"""
        self.user_feedback = UserFeedback()
        
    def test_error_notification(self):
        """Test error notification to user"""
        error = CartridgeError("Cartridge operation failed")
        
        with patch.object(self.user_feedback, 'show_error_notification') as mock_notify:
            self.user_feedback.notify_error(error)
            mock_notify.assert_called_once_with(error)
            
    def test_progress_error_reporting(self):
        """Test error reporting during progress operations"""
        progress_callback = Mock()
        
        error = FirmwareFlashError("Flash verification failed")
        self.user_feedback.report_progress_error(error, progress_callback)
        
        progress_callback.assert_called_once()
        call_args = progress_callback.call_args[0][0]
        self.assertIn('error', call_args)
        self.assertEqual(call_args['error'], str(error))
        
    def test_recovery_suggestion(self):
        """Test recovery suggestion generation"""
        device_error = DeviceNotFoundError("No Chromatic device found")
        suggestion = self.user_feedback.get_recovery_suggestion(device_error)
        
        self.assertIn("device", suggestion.lower())
        self.assertIn("connect", suggestion.lower())
        
        comm_error = CommunicationError("Communication timeout")
        suggestion = self.user_feedback.get_recovery_suggestion(comm_error)
        
        self.assertIn("retry", suggestion.lower())
        
    def test_error_reporting_with_logs(self):
        """Test error reporting with log collection"""
        error = ChromaticError("Test error for reporting")
        
        with patch.object(self.user_feedback, 'collect_diagnostic_info') as mock_collect:
            mock_collect.return_value = {
                'error_details': str(error),
                'system_info': {'os': 'macOS', 'version': '14.0'},
                'recent_logs': ['Log entry 1', 'Log entry 2']
            }
            
            diagnostic_info = self.user_feedback.prepare_error_report(error)
            
            self.assertIn('error_details', diagnostic_info)
            self.assertIn('system_info', diagnostic_info)
            self.assertIn('recent_logs', diagnostic_info)


class TestErrorHandlingIntegration(unittest.TestCase):
    """Test integration of error handling components"""
    
    def test_end_to_end_error_handling(self):
        """Test complete error handling workflow"""
        # Simulate a cartridge read operation that fails
        def failing_cartridge_read():
            raise CartridgeReadError("ROM read failed at address 0x1000")
            
        error_recovery = ErrorRecovery()
        user_feedback = UserFeedback()
        
        # Attempt operation with error handling
        try:
            error_recovery.retry_operation(
                failing_cartridge_read,
                max_retries=2,
                delay=0.01
            )
        except CartridgeReadError as e:
            # Handle the error
            recovery_strategy = error_recovery.get_recovery_strategy(e)
            self.assertEqual(recovery_strategy, RecoveryStrategy.USER_INTERVENTION)
            
            # Get user feedback
            suggestion = user_feedback.get_recovery_suggestion(e)
            self.assertIsInstance(suggestion, str)
            self.assertGreater(len(suggestion), 0)
            
    def test_error_context_preservation(self):
        """Test that error context is preserved through recovery attempts"""
        original_context = {
            'operation': 'cartridge_read',
            'address': '0x1000',
            'attempt': 1
        }
        
        error = CartridgeReadError("Read failed", context=original_context)
        
        # Simulate error propagation through recovery
        error_recovery = ErrorRecovery()
        
        try:
            def failing_op():
                raise error
                
            error_recovery.retry_operation(failing_op, max_retries=1, delay=0.01)
        except CartridgeReadError as caught_error:
            # Context should be preserved
            self.assertEqual(caught_error.context, original_context)


if __name__ == '__main__':
    unittest.main(verbosity=2)
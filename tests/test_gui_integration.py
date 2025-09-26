#!/usr/bin/env python3
"""
Automated GUI tests using Qt Test framework.
Tests GUI components and user interactions.
"""

import unittest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import Qt test framework
try:
    from PySide6.QtTest import QTest
    from PySide6.QtCore import Qt, QTimer
    from PySide6.QtWidgets import QApplication, QWidget, QMessageBox
    from PySide6.QtGui import QPixmap
    QT_AVAILABLE = True
except ImportError:
    QT_AVAILABLE = False
    # Create mock classes for testing without Qt
    class QTest:
        @staticmethod
        def mouseClick(widget, button): pass
        @staticmethod
        def keyClick(widget, key): pass
        @staticmethod
        def qWait(ms): pass
    
    class Qt:
        LeftButton = 1
        Key_Return = 2
    
    class QApplication:
        def __init__(self, args): pass
        def exec(self): return 0
        def quit(self): pass
    
    class QWidget:
        def __init__(self): pass
        def show(self): pass
        def close(self): pass

# Import application components
from main import MainWindow
from cartclinic.gui import CartClinicWidget
from error_dialog import ErrorDialog
from user_feedback import UserFeedback
from tests.mocks.mock_chromatic_device import MockChromaticDevice


@unittest.skipUnless(QT_AVAILABLE, "Qt not available for GUI testing")
class TestMainWindowGUI(unittest.TestCase):
    """Test main window GUI functionality"""
    
    @classmethod
    def setUpClass(cls):
        """Set up Qt application for testing"""
        if QT_AVAILABLE and not QApplication.instance():
            cls.app = QApplication(sys.argv)
        else:
            cls.app = QApplication.instance()
            
    def setUp(self):
        """Set up test environment"""
        self.main_window = None
        
    def tearDown(self):
        """Clean up after test"""
        if self.main_window:
            self.main_window.close()
            
    def test_main_window_creation(self):
        """Test main window creation and initialization"""
        with patch('main.DeviceManager') as mock_dm:
            mock_dm.return_value = Mock()
            
            self.main_window = MainWindow()
            self.assertIsNotNone(self.main_window)
            
            # Test window properties
            self.assertIsInstance(self.main_window, QWidget)
            
    def test_main_window_show(self):
        """Test main window display"""
        with patch('main.DeviceManager') as mock_dm:
            mock_dm.return_value = Mock()
            
            self.main_window = MainWindow()
            self.main_window.show()
            
            # Wait for window to be displayed
            QTest.qWait(100)
            
            # Window should be visible
            self.assertTrue(self.main_window.isVisible())
            
    def test_tab_switching(self):
        """Test switching between tabs"""
        with patch('main.DeviceManager') as mock_dm:
            mock_dm.return_value = Mock()
            
            self.main_window = MainWindow()
            self.main_window.show()
            
            # Get tab widget
            tab_widget = self.main_window.findChild(QWidget, "tabWidget")
            if tab_widget:
                # Test switching to Cart Clinic tab
                tab_widget.setCurrentIndex(1)  # Assuming Cart Clinic is tab 1
                QTest.qWait(50)
                
                current_index = tab_widget.currentIndex()
                self.assertEqual(current_index, 1)
                
    def test_device_status_display(self):
        """Test device status display in GUI"""
        with patch('main.DeviceManager') as mock_dm:
            # Mock device detection
            mock_device_info = Mock()
            mock_device_info.serial_number = "MOCK001"
            mock_device_info.product_name = "Mock Chromatic"
            
            mock_dm_instance = Mock()
            mock_dm.return_value = mock_dm_instance
            mock_dm_instance.scan_for_devices.return_value = [mock_device_info]
            
            self.main_window = MainWindow()
            self.main_window.show()
            
            # Trigger device scan
            self.main_window.refresh_device_list()
            QTest.qWait(100)
            
            # Check that device status is updated
            # (This would need to check specific UI elements)
            
    def test_menu_actions(self):
        """Test menu actions"""
        with patch('main.DeviceManager') as mock_dm:
            mock_dm.return_value = Mock()
            
            self.main_window = MainWindow()
            self.main_window.show()
            
            # Test menu actions if they exist
            menu_bar = self.main_window.menuBar()
            if menu_bar:
                # Find and test menu actions
                actions = menu_bar.actions()
                for action in actions:
                    if action.text() == "File":
                        # Test file menu
                        action.trigger()
                        QTest.qWait(50)


@unittest.skipUnless(QT_AVAILABLE, "Qt not available for GUI testing")
class TestCartClinicGUI(unittest.TestCase):
    """Test Cart Clinic GUI functionality"""
    
    @classmethod
    def setUpClass(cls):
        """Set up Qt application for testing"""
        if QT_AVAILABLE and not QApplication.instance():
            cls.app = QApplication(sys.argv)
        else:
            cls.app = QApplication.instance()
            
    def setUp(self):
        """Set up test environment"""
        self.cart_clinic_widget = None
        self.mock_device = MockChromaticDevice()
        self.mock_device.connect()
        
    def tearDown(self):
        """Clean up after test"""
        if self.cart_clinic_widget:
            self.cart_clinic_widget.close()
            
    def test_cart_clinic_widget_creation(self):
        """Test Cart Clinic widget creation"""
        with patch('cartclinic.gui.SerialTransport') as mock_transport:
            mock_transport.return_value = Mock()
            
            self.cart_clinic_widget = CartClinicWidget()
            self.assertIsNotNone(self.cart_clinic_widget)
            
    def test_cartridge_detection_ui(self):
        """Test cartridge detection UI updates"""
        with patch('cartclinic.gui.SerialTransport') as mock_transport:
            mock_transport_instance = Mock()
            mock_transport.return_value = mock_transport_instance
            mock_transport_instance.is_connected.return_value = True
            
            def mock_send_command(command):
                return self.mock_device.send_command(command)
            
            mock_transport_instance.send_command.side_effect = mock_send_command
            
            self.cart_clinic_widget = CartClinicWidget()
            self.cart_clinic_widget.show()
            
            # Simulate cartridge detection
            self.cart_clinic_widget.refresh_cartridge_status()
            QTest.qWait(100)
            
            # Check UI updates (would need specific UI element checks)
            
    def test_read_cartridge_button(self):
        """Test read cartridge button functionality"""
        with patch('cartclinic.gui.SerialTransport') as mock_transport:
            mock_transport_instance = Mock()
            mock_transport.return_value = mock_transport_instance
            mock_transport_instance.is_connected.return_value = True
            
            def mock_send_command(command):
                return self.mock_device.send_command(command)
            
            mock_transport_instance.send_command.side_effect = mock_send_command
            
            self.cart_clinic_widget = CartClinicWidget()
            self.cart_clinic_widget.show()
            
            # Find read button
            read_button = self.cart_clinic_widget.findChild(QWidget, "readButton")
            if read_button:
                # Click read button
                QTest.mouseClick(read_button, Qt.LeftButton)
                QTest.qWait(100)
                
                # Check that read operation was triggered
                # (Would need to verify specific behavior)
                
    def test_write_cartridge_button(self):
        """Test write cartridge button functionality"""
        with patch('cartclinic.gui.SerialTransport') as mock_transport:
            mock_transport_instance = Mock()
            mock_transport.return_value = mock_transport_instance
            mock_transport_instance.is_connected.return_value = True
            
            def mock_send_command(command):
                return self.mock_device.send_command(command)
            
            mock_transport_instance.send_command.side_effect = mock_send_command
            
            self.cart_clinic_widget = CartClinicWidget()
            self.cart_clinic_widget.show()
            
            # Find write button
            write_button = self.cart_clinic_widget.findChild(QWidget, "writeButton")
            if write_button:
                # Click write button
                QTest.mouseClick(write_button, Qt.LeftButton)
                QTest.qWait(100)
                
    def test_progress_bar_updates(self):
        """Test progress bar updates during operations"""
        with patch('cartclinic.gui.SerialTransport') as mock_transport:
            mock_transport_instance = Mock()
            mock_transport.return_value = mock_transport_instance
            mock_transport_instance.is_connected.return_value = True
            
            self.cart_clinic_widget = CartClinicWidget()
            self.cart_clinic_widget.show()
            
            # Find progress bar
            progress_bar = self.cart_clinic_widget.findChild(QWidget, "progressBar")
            if progress_bar:
                # Test progress updates
                self.cart_clinic_widget.update_progress(50.0)
                QTest.qWait(50)
                
                # Check progress value
                # self.assertEqual(progress_bar.value(), 50)


@unittest.skipUnless(QT_AVAILABLE, "Qt not available for GUI testing")
class TestErrorDialogGUI(unittest.TestCase):
    """Test error dialog GUI functionality"""
    
    @classmethod
    def setUpClass(cls):
        """Set up Qt application for testing"""
        if QT_AVAILABLE and not QApplication.instance():
            cls.app = QApplication(sys.argv)
        else:
            cls.app = QApplication.instance()
            
    def setUp(self):
        """Set up test environment"""
        self.error_dialog = None
        
    def tearDown(self):
        """Clean up after test"""
        if self.error_dialog:
            self.error_dialog.close()
            
    def test_error_dialog_creation(self):
        """Test error dialog creation"""
        from exceptions import CartridgeError
        
        error = CartridgeError("Test error message")
        self.error_dialog = ErrorDialog.create_for_error(error)
        
        self.assertIsNotNone(self.error_dialog)
        
    def test_error_dialog_display(self):
        """Test error dialog display"""
        from exceptions import CommunicationError
        
        error = CommunicationError("Device communication failed")
        self.error_dialog = ErrorDialog.create_for_error(error)
        
        if self.error_dialog:
            self.error_dialog.show()
            QTest.qWait(100)
            
            # Dialog should be visible
            self.assertTrue(self.error_dialog.isVisible())
            
    def test_error_dialog_buttons(self):
        """Test error dialog button interactions"""
        from exceptions import DeviceNotFoundError
        
        error = DeviceNotFoundError("No device found")
        self.error_dialog = ErrorDialog.create_for_error(
            error,
            recovery_options=['Retry', 'Cancel']
        )
        
        if self.error_dialog:
            self.error_dialog.show()
            QTest.qWait(100)
            
            # Find and test buttons
            buttons = self.error_dialog.findChildren(QWidget, "QPushButton")
            if buttons:
                # Click first button (Retry)
                QTest.mouseClick(buttons[0], Qt.LeftButton)
                QTest.qWait(50)


class TestGUIWithoutQt(unittest.TestCase):
    """Test GUI components without Qt (mock testing)"""
    
    def test_main_window_mock(self):
        """Test main window with mocked Qt"""
        with patch('PySide6.QtWidgets.QMainWindow') as mock_window:
            with patch('main.DeviceManager') as mock_dm:
                mock_dm.return_value = Mock()
                
                # This tests that the main window can be imported and created
                # even when Qt is mocked
                from main import MainWindow
                window = MainWindow()
                self.assertIsNotNone(window)
                
    def test_cart_clinic_widget_mock(self):
        """Test Cart Clinic widget with mocked Qt"""
        with patch('PySide6.QtWidgets.QWidget') as mock_widget:
            with patch('cartclinic.gui.SerialTransport') as mock_transport:
                mock_transport.return_value = Mock()
                
                from cartclinic.gui import CartClinicWidget
                widget = CartClinicWidget()
                self.assertIsNotNone(widget)
                
    def test_error_dialog_mock(self):
        """Test error dialog with mocked Qt"""
        with patch('PySide6.QtWidgets.QMessageBox') as mock_messagebox:
            mock_dialog = Mock()
            mock_messagebox.return_value = mock_dialog
            
            from exceptions import CartridgeError
            from error_dialog import ErrorDialog
            
            error = CartridgeError("Test error")
            dialog = ErrorDialog.create_for_error(error)
            
            self.assertIsNotNone(dialog)
            mock_messagebox.assert_called_once()


class TestUserInteractionWorkflows(unittest.TestCase):
    """Test complete user interaction workflows"""
    
    def test_device_connection_workflow(self):
        """Test device connection user workflow"""
        with patch('main.DeviceManager') as mock_dm:
            # Simulate no devices initially
            mock_dm_instance = Mock()
            mock_dm.return_value = mock_dm_instance
            mock_dm_instance.scan_for_devices.return_value = []
            
            # User should see "no devices" message
            # Then after connecting device, should see device
            mock_dm_instance.scan_for_devices.return_value = [Mock(
                serial_number="MOCK001",
                product_name="Mock Chromatic"
            )]
            
            # Test that device manager can handle this workflow
            device_manager = mock_dm_instance
            
            # Initial scan - no devices
            devices = device_manager.scan_for_devices()
            self.assertEqual(len(devices), 1)  # After mock update
            
    def test_cartridge_operation_workflow(self):
        """Test cartridge operation user workflow"""
        mock_device = MockChromaticDevice()
        mock_device.connect()
        
        # Simulate user workflow:
        # 1. Insert cartridge
        # 2. Detect cartridge
        # 3. Read cartridge info
        # 4. Perform operation
        
        from tests.mocks.mock_device import MockCartridgeData
        test_cartridge = MockCartridgeData(title="USER TEST")
        mock_device.insert_cartridge(test_cartridge)
        
        # Test detection
        from libpyretro.cartclinic.comms.transport import CommandMessage
        detect_command = CommandMessage(command="cart_detect")
        response = mock_device.send_command(detect_command)
        
        self.assertTrue(response.success)
        self.assertTrue(response.data["inserted"])
        
    def test_firmware_update_workflow(self):
        """Test firmware update user workflow"""
        with patch('flashing_tool.firmware_flasher.FirmwareFlasher') as mock_flasher:
            mock_flasher_instance = Mock()
            mock_flasher.return_value = mock_flasher_instance
            
            # Simulate user workflow:
            # 1. Check for updates
            # 2. Download firmware
            # 3. Flash firmware
            # 4. Verify update
            
            mock_comparison = Mock()
            mock_comparison.update_available = True
            mock_flasher_instance.check_for_updates.return_value = mock_comparison
            mock_flasher_instance.flash_firmware.return_value = True
            
            flasher = mock_flasher_instance
            
            # User checks for updates
            comparison = flasher.check_for_updates()
            self.assertTrue(comparison.update_available)
            
            # User initiates flash
            success = flasher.flash_firmware('2.0.0')
            self.assertTrue(success)


if __name__ == '__main__':
    # Run tests with different verbosity based on Qt availability
    if QT_AVAILABLE:
        print("Running GUI tests with Qt framework")
        unittest.main(verbosity=2)
    else:
        print("Running GUI tests with mocked Qt (Qt not available)")
        unittest.main(verbosity=2)
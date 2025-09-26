#!/usr/bin/env python3
"""
Unit tests for startup validation and dependency checking.
Tests system compatibility checks and dependency validation.
"""

import unittest
import sys
import tempfile
import subprocess
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from startup_validator import (
    SystemValidator, DependencyValidator, ToolValidator, StartupValidator,
    ValidationResult, ValidationCheck
)
from setup_wizard import SetupWizard


class TestSystemValidator(unittest.TestCase):
    """Test system validation functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.validator = SystemValidator()
        
    def test_python_version_validation(self):
        """Test Python version validation"""
        check = self.validator.validate_python_version()
        
        self.assertIsInstance(check, ValidationCheck)
        self.assertEqual(check.name, "Python Version")
        
        # Current Python should be supported (3.8+)
        self.assertIn(check.result, [ValidationResult.PASS, ValidationResult.FAIL])
        
    @patch('platform.system')
    def test_macos_version_validation_non_macos(self, mock_system):
        """Test macOS version validation on non-macOS system"""
        mock_system.return_value = 'Linux'
        
        check = self.validator.validate_macos_version()
        
        self.assertEqual(check.result, ValidationResult.SKIP)
        self.assertIn("Not running on macOS", check.message)
        
    @patch('platform.system')
    @patch('subprocess.check_output')
    def test_macos_version_validation_supported(self, mock_subprocess, mock_system):
        """Test macOS version validation with supported version"""
        mock_system.return_value = 'Darwin'
        mock_subprocess.return_value = '12.0.1'
        
        check = self.validator.validate_macos_version()
        
        self.assertEqual(check.result, ValidationResult.PASS)
        self.assertIn("12.0.1", check.message)
        
    @patch('platform.system')
    @patch('subprocess.check_output')
    def test_macos_version_validation_old(self, mock_subprocess, mock_system):
        """Test macOS version validation with old version"""
        mock_system.return_value = 'Darwin'
        mock_subprocess.return_value = '10.14.6'
        
        check = self.validator.validate_macos_version()
        
        self.assertEqual(check.result, ValidationResult.WARN)
        self.assertIn("compatibility issues", check.message)
        
    @patch('platform.system')
    def test_usb_permissions_non_macos(self, mock_system):
        """Test USB permissions check on non-macOS"""
        mock_system.return_value = 'Linux'
        
        check = self.validator.validate_usb_permissions()
        
        self.assertEqual(check.result, ValidationResult.SKIP)
        
    @patch('platform.system')
    @patch('usb.core.find')
    def test_usb_permissions_working(self, mock_find, mock_system):
        """Test USB permissions when working"""
        mock_system.return_value = 'Darwin'
        mock_find.return_value = [Mock(), Mock()]  # Mock 2 devices
        
        check = self.validator.validate_usb_permissions()
        
        self.assertEqual(check.result, ValidationResult.PASS)
        self.assertIn("found 2 devices", check.message)
        
    @patch('os.statvfs')
    def test_disk_space_sufficient(self, mock_statvfs):
        """Test disk space check with sufficient space"""
        # Mock 500MB available
        mock_stat = Mock()
        mock_stat.f_frsize = 4096
        mock_stat.f_bavail = 128000  # 500MB in 4KB blocks
        mock_statvfs.return_value = mock_stat
        
        check = self.validator.validate_disk_space()
        
        self.assertEqual(check.result, ValidationResult.PASS)
        self.assertIn("500.0 MB", check.message)
        
    @patch('os.statvfs')
    def test_disk_space_low(self, mock_statvfs):
        """Test disk space check with low space"""
        # Mock 50MB available
        mock_stat = Mock()
        mock_stat.f_frsize = 4096
        mock_stat.f_bavail = 12800  # 50MB in 4KB blocks
        mock_statvfs.return_value = mock_stat
        
        check = self.validator.validate_disk_space()
        
        self.assertEqual(check.result, ValidationResult.WARN)
        self.assertIn("Low disk space", check.message)
        
    def test_run_all_checks(self):
        """Test running all system checks"""
        checks = self.validator.run_all_checks()
        
        self.assertIsInstance(checks, list)
        self.assertGreater(len(checks), 0)
        
        # All checks should be ValidationCheck instances
        for check in checks:
            self.assertIsInstance(check, ValidationCheck)


class TestDependencyValidator(unittest.TestCase):
    """Test dependency validation functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.validator = DependencyValidator()
        
    def test_validate_existing_package(self):
        """Test validation of existing package"""
        # Test with a standard library module that should exist
        check = self.validator.validate_package('sys')
        
        self.assertEqual(check.result, ValidationResult.PASS)
        self.assertIn("sys", check.message)
        
    def test_validate_missing_package(self):
        """Test validation of missing package"""
        check = self.validator.validate_package('nonexistent_package_12345')
        
        self.assertEqual(check.result, ValidationResult.FAIL)
        self.assertIn("not installed", check.message)
        self.assertIn("pip install", check.fix_suggestion)
        
    def test_validate_package_with_version(self):
        """Test package validation with version checking"""
        # Mock a package with version
        with patch('importlib.import_module') as mock_import:
            mock_module = Mock()
            mock_module.__version__ = '2.0.0'
            mock_import.return_value = mock_module
            
            check = self.validator.validate_package('mock_package', '1.0.0')
            
            self.assertEqual(check.result, ValidationResult.PASS)
            self.assertIn("2.0.0", check.message)
            
    def test_validate_package_old_version(self):
        """Test package validation with old version"""
        with patch('importlib.import_module') as mock_import:
            mock_module = Mock()
            mock_module.__version__ = '1.0.0'
            mock_import.return_value = mock_module
            
            check = self.validator.validate_package('mock_package', '2.0.0')
            
            self.assertEqual(check.result, ValidationResult.WARN)
            self.assertIn("below minimum", check.message)
            
    def test_requirements_file_exists(self):
        """Test requirements file validation when file exists"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("PySide6>=6.0.0\npyserial>=3.0\n")
            temp_file = f.name
            
        try:
            with patch.object(Path, '__truediv__') as mock_div:
                mock_div.return_value = Path(temp_file)
                
                check = self.validator.validate_requirements_file()
                
                self.assertEqual(check.result, ValidationResult.PASS)
                self.assertIn("2 packages", check.message)
        finally:
            Path(temp_file).unlink()
            
    def test_requirements_file_missing(self):
        """Test requirements file validation when file missing"""
        with patch.object(Path, 'exists') as mock_exists:
            mock_exists.return_value = False
            
            check = self.validator.validate_requirements_file()
            
            self.assertEqual(check.result, ValidationResult.WARN)
            self.assertIn("not found", check.message)
            
    def test_run_all_checks(self):
        """Test running all dependency checks"""
        checks = self.validator.run_all_checks()
        
        self.assertIsInstance(checks, list)
        self.assertGreater(len(checks), 1)  # At least requirements file + packages
        
        # Should include requirements file check
        req_checks = [c for c in checks if c.name == "Requirements File"]
        self.assertEqual(len(req_checks), 1)


class TestToolValidator(unittest.TestCase):
    """Test external tool validation functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.validator = ToolValidator()
        
    @patch('subprocess.run')
    def test_validate_tool_available(self, mock_run):
        """Test validation of available tool"""
        mock_run.return_value = Mock(
            returncode=0,
            stdout="mock_tool v1.0.0\n",
            stderr=""
        )
        
        tool_info = {
            'description': 'Mock tool',
            'install_hint': 'Install mock tool'
        }
        
        check = self.validator.validate_tool('mock_tool', tool_info)
        
        self.assertEqual(check.result, ValidationResult.PASS)
        self.assertIn("mock_tool v1.0.0", check.message)
        
    @patch('subprocess.run')
    def test_validate_tool_missing(self, mock_run):
        """Test validation of missing tool"""
        mock_run.side_effect = FileNotFoundError()
        
        tool_info = {
            'description': 'Mock tool',
            'install_hint': 'Install mock tool'
        }
        
        check = self.validator.validate_tool('missing_tool', tool_info)
        
        self.assertEqual(check.result, ValidationResult.WARN)
        self.assertIn("not found", check.message)
        self.assertEqual(check.fix_suggestion, 'Install mock tool')
        
    def test_run_all_checks(self):
        """Test running all tool checks"""
        checks = self.validator.run_all_checks()
        
        self.assertIsInstance(checks, list)
        self.assertGreater(len(checks), 0)
        
        # Should check for openFPGALoader and esptool
        tool_names = [c.name for c in checks]
        self.assertIn("Tool: openFPGALoader", tool_names)
        self.assertIn("Tool: esptool.py", tool_names)


class TestStartupValidator(unittest.TestCase):
    """Test main startup validator"""
    
    def setUp(self):
        """Set up test environment"""
        self.validator = StartupValidator()
        
    def test_run_all_validations(self):
        """Test running all validations"""
        success, checks = self.validator.run_all_validations()
        
        self.assertIsInstance(success, bool)
        self.assertIsInstance(checks, list)
        self.assertGreater(len(checks), 0)
        
        # Should include checks from all validators
        check_names = [c.name for c in checks]
        self.assertIn("Python Version", check_names)
        self.assertIn("Requirements File", check_names)
        
    def test_print_validation_report(self):
        """Test validation report printing"""
        # Create mock checks
        checks = [
            ValidationCheck("Test Pass", ValidationResult.PASS, "Test passed"),
            ValidationCheck("Test Warn", ValidationResult.WARN, "Test warning", fix_suggestion="Fix it"),
            ValidationCheck("Test Fail", ValidationResult.FAIL, "Test failed", fix_suggestion="Fix it"),
            ValidationCheck("Test Skip", ValidationResult.SKIP, "Test skipped")
        ]
        
        # This should not raise an exception
        success = self.validator.print_validation_report(checks)
        
        # Should return False due to failure
        self.assertFalse(success)
        
    def test_generate_setup_script(self):
        """Test setup script generation"""
        checks = [
            ValidationCheck("Package: missing_pkg", ValidationResult.FAIL, "Not installed"),
            ValidationCheck("Tool: missing_tool", ValidationResult.WARN, "Not found", 
                          fix_suggestion="Install missing_tool")
        ]
        
        script = self.validator.generate_setup_script(checks)
        
        self.assertIsInstance(script, str)
        self.assertIn("pip install missing_pkg", script)
        self.assertIn("Install missing_tool", script)


class TestSetupWizard(unittest.TestCase):
    """Test setup wizard functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.wizard = SetupWizard()
        
    def test_wizard_creation(self):
        """Test setup wizard creation"""
        self.assertIsNotNone(self.wizard)
        self.assertIn('platform', self.wizard.system_info)
        
    @patch('builtins.input')
    def test_ask_yes_no_default_yes(self, mock_input):
        """Test yes/no question with default yes"""
        mock_input.return_value = ''  # Empty input (use default)
        
        result = self.wizard.ask_yes_no("Test question?", default=True)
        
        self.assertTrue(result)
        
    @patch('builtins.input')
    def test_ask_yes_no_explicit_no(self, mock_input):
        """Test yes/no question with explicit no"""
        mock_input.return_value = 'n'
        
        result = self.wizard.ask_yes_no("Test question?", default=True)
        
        self.assertFalse(result)
        
    @patch('builtins.input')
    def test_ask_choice_default(self, mock_input):
        """Test choice question with default"""
        mock_input.return_value = ''  # Empty input (use default)
        
        choices = ["Option 1", "Option 2", "Option 3"]
        result = self.wizard.ask_choice("Choose option:", choices, default=1)
        
        self.assertEqual(result, 1)
        
    @patch('builtins.input')
    def test_ask_choice_explicit(self, mock_input):
        """Test choice question with explicit choice"""
        mock_input.return_value = '3'
        
        choices = ["Option 1", "Option 2", "Option 3"]
        result = self.wizard.ask_choice("Choose option:", choices, default=0)
        
        self.assertEqual(result, 2)  # 0-indexed
        
    def test_check_python_dependencies(self):
        """Test Python dependency checking"""
        installed, missing = self.wizard.check_python_dependencies()
        
        self.assertIsInstance(installed, list)
        self.assertIsInstance(missing, list)
        
        # sys should always be installed
        # (though it might not be in the required packages list)
        
    @patch('subprocess.run')
    def test_install_python_dependencies_success(self, mock_run):
        """Test successful Python dependency installation"""
        mock_run.return_value = Mock(returncode=0)
        
        with patch.object(self.wizard, 'ask_yes_no', return_value=True):
            result = self.wizard.install_python_dependencies(['test_package'])
            
            self.assertTrue(result)
            mock_run.assert_called_once()
            
    @patch('subprocess.run')
    def test_install_python_dependencies_failure(self, mock_run):
        """Test failed Python dependency installation"""
        mock_run.side_effect = subprocess.CalledProcessError(1, 'pip')
        
        with patch.object(self.wizard, 'ask_yes_no', return_value=True):
            result = self.wizard.install_python_dependencies(['test_package'])
            
            self.assertFalse(result)
            
    def test_check_external_tools(self):
        """Test external tool checking"""
        tools_status = self.wizard.check_external_tools()
        
        self.assertIsInstance(tools_status, dict)
        self.assertIn('openFPGALoader', tools_status)
        self.assertIn('esptool.py', tools_status)
        
        for tool, status in tools_status.items():
            self.assertIsInstance(status, bool)


class TestValidationIntegration(unittest.TestCase):
    """Test integration of validation components"""
    
    def test_full_validation_workflow(self):
        """Test complete validation workflow"""
        validator = StartupValidator()
        
        # Run validation
        success, checks = validator.run_all_validations()
        
        # Should get results
        self.assertIsInstance(success, bool)
        self.assertIsInstance(checks, list)
        
        # Should have checks from all validators
        check_categories = set()
        for check in checks:
            if check.name.startswith("Package:"):
                check_categories.add("packages")
            elif check.name.startswith("Tool:"):
                check_categories.add("tools")
            elif check.name in ["Python Version", "macOS Version", "USB Permissions", "Disk Space"]:
                check_categories.add("system")
            elif check.name == "Requirements File":
                check_categories.add("requirements")
                
        # Should have at least system and requirements checks
        self.assertIn("system", check_categories)
        self.assertIn("requirements", check_categories)
        
    def test_validation_with_mock_failures(self):
        """Test validation with simulated failures"""
        validator = StartupValidator()
        
        # Mock some failures
        with patch.object(validator.dependency_validator, 'validate_package') as mock_validate:
            mock_validate.return_value = ValidationCheck(
                "Package: test", ValidationResult.FAIL, "Test failure"
            )
            
            success, checks = validator.run_all_validations()
            
            # Should fail due to mocked failure
            self.assertFalse(success)
            
            # Should have failure in checks
            failures = [c for c in checks if c.result == ValidationResult.FAIL]
            self.assertGreater(len(failures), 0)


if __name__ == '__main__':
    unittest.main(verbosity=2)
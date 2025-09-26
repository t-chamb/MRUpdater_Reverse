#!/usr/bin/env python3
"""
Comprehensive test runner for MRUpdater.
Runs unit tests, integration tests, and startup validation tests.
"""

import sys
import unittest
import logging
import time
from pathlib import Path
from io import StringIO

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Configure logging for tests
logging.basicConfig(
    level=logging.WARNING,
    format='%(name)s - %(levelname)s - %(message)s'
)


class ComprehensiveTestResult(unittest.TextTestResult):
    """Custom test result class for comprehensive testing"""
    
    def __init__(self, stream, descriptions, verbosity):
        super().__init__(stream, descriptions, verbosity)
        self.success_count = 0
        self.test_times = {}
        self.slow_tests = []
        self.start_time = None
        
    def startTest(self, test):
        super().startTest(test)
        self.start_time = time.time()
        
    def stopTest(self, test):
        super().stopTest(test)
        if self.start_time:
            test_time = time.time() - self.start_time
            self.test_times[str(test)] = test_time
            
            # Track slow tests (>2 seconds)
            if test_time > 2.0:
                self.slow_tests.append((str(test), test_time))
        
    def addSuccess(self, test):
        super().addSuccess(test)
        self.success_count += 1
        if self.verbosity > 1:
            test_time = self.test_times.get(str(test), 0)
            self.stream.write("✓ ")
            self.stream.write(self.getDescription(test))
            if test_time > 0.5:  # Show time for slower tests
                self.stream.write(f" ({test_time:.2f}s)")
            self.stream.writeln("")
            
    def addError(self, test, err):
        super().addError(test, err)
        if self.verbosity > 1:
            self.stream.write("✗ ")
            self.stream.writeln(self.getDescription(test))
            
    def addFailure(self, test, err):
        super().addFailure(test, err)
        if self.verbosity > 1:
            self.stream.write("✗ ")
            self.stream.writeln(self.getDescription(test))
            
    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        if self.verbosity > 1:
            self.stream.write("⚠ ")
            self.stream.writeln(f"{self.getDescription(test)} (skipped: {reason})")


class ComprehensiveTestRunner(unittest.TextTestRunner):
    """Custom test runner for comprehensive testing"""
    
    resultclass = ComprehensiveTestResult
    
    def _makeResult(self):
        return self.resultclass(self.stream, self.descriptions, self.verbosity)


def discover_all_tests():
    """Discover all test modules"""
    test_dir = Path(__file__).parent
    loader = unittest.TestLoader()
    
    # Discover all test files
    suite = loader.discover(
        start_dir=str(test_dir),
        pattern='test_*.py',
        top_level_dir=str(test_dir.parent)
    )
    
    return suite


def discover_unit_tests():
    """Discover unit test modules"""
    test_dir = Path(__file__).parent
    loader = unittest.TestLoader()
    
    unit_test_patterns = [
        'test_cartridge_operations.py',
        'test_firmware_flashing.py',
        'test_error_handling.py',
        'test_startup_validation.py'
    ]
    
    suite = unittest.TestSuite()
    
    for pattern in unit_test_patterns:
        try:
            module_suite = loader.discover(
                start_dir=str(test_dir),
                pattern=pattern,
                top_level_dir=str(test_dir.parent)
            )
            suite.addTest(module_suite)
        except Exception as e:
            print(f"Warning: Could not load {pattern}: {e}")
    
    return suite


def discover_integration_tests():
    """Discover integration test modules"""
    test_dir = Path(__file__).parent
    loader = unittest.TestLoader()
    
    integration_patterns = [
        'test_integration_workflows.py',
        'test_gui_integration.py'
    ]
    
    suite = unittest.TestSuite()
    
    for pattern in integration_patterns:
        try:
            module_suite = loader.discover(
                start_dir=str(test_dir),
                pattern=pattern,
                top_level_dir=str(test_dir.parent)
            )
            suite.addTest(module_suite)
        except Exception as e:
            print(f"Warning: Could not load {pattern}: {e}")
    
    return suite


def check_test_environment():
    """Check test environment and dependencies"""
    print("Checking test environment...")
    
    dependencies = {
        'unittest': True,  # Standard library
        'unittest.mock': True,  # Standard library
        'PySide6': False,
        'pathlib': True,  # Standard library
    }
    
    # Check optional dependencies
    try:
        import PySide6
        dependencies['PySide6'] = True
    except ImportError:
        pass
    
    print("Test Dependencies:")
    for dep, available in dependencies.items():
        status = "✓" if available else "✗"
        print(f"  {status} {dep}")
    
    return dependencies


def print_comprehensive_summary(result, test_type="All"):
    """Print detailed test summary"""
    total_tests = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    skipped = len(result.skipped)
    successes = result.success_count
    
    print("\n" + "="*70)
    print(f"{test_type.upper()} TESTS SUMMARY")
    print("="*70)
    print(f"Total tests run: {total_tests}")
    print(f"Successes: {successes} ✓")
    print(f"Failures: {failures} ✗")
    print(f"Errors: {errors} ✗")
    print(f"Skipped: {skipped} ⚠")
    
    # Show timing information
    if hasattr(result, 'test_times') and result.test_times:
        total_time = sum(result.test_times.values())
        avg_time = total_time / len(result.test_times)
        print(f"Total time: {total_time:.2f}s")
        print(f"Average time per test: {avg_time:.3f}s")
        
        # Show slow tests
        if result.slow_tests:
            print(f"\nSlow tests (>2s):")
            for test_name, test_time in sorted(result.slow_tests, key=lambda x: x[1], reverse=True):
                print(f"  {test_time:.2f}s - {test_name}")
    
    # Show failures and errors
    if failures > 0:
        print(f"\nFAILURES ({failures}):")
        for test, traceback in result.failures:
            print(f"  - {test}")
            # Show first few lines of traceback
            lines = traceback.split('\n')
            for line in lines[:3]:
                if line.strip():
                    print(f"    {line}")
            if len(lines) > 3:
                print(f"    ... (truncated)")
            
    if errors > 0:
        print(f"\nERRORS ({errors}):")
        for test, traceback in result.errors:
            print(f"  - {test}")
            # Show first few lines of traceback
            lines = traceback.split('\n')
            for line in lines[:3]:
                if line.strip():
                    print(f"    {line}")
            if len(lines) > 3:
                print(f"    ... (truncated)")
                
    if skipped > 0:
        print(f"\nSKIPPED ({skipped}):")
        for test, reason in result.skipped:
            print(f"  - {test}: {reason}")
            
    # Calculate success rate
    success_rate = (successes / total_tests * 100) if total_tests > 0 else 0
    print(f"\nSuccess rate: {success_rate:.1f}%")
    
    # Overall assessment
    if success_rate == 100:
        print("🎉 All tests passed!")
        return True
    elif success_rate >= 90:
        print("✅ Most tests passed - excellent!")
        return True
    elif success_rate >= 75:
        print("✅ Most tests passed - good")
        return True
    elif success_rate >= 50:
        print("⚠️  Many tests passed - needs attention")
        return False
    else:
        print("❌ Many tests failed - requires immediate attention")
        return False


def run_test_suite(suite, test_type, verbosity=1, failfast=False):
    """Run a test suite and return results"""
    if suite.countTestCases() == 0:
        print(f"No {test_type.lower()} tests found!")
        return None
        
    print(f"\nRunning {suite.countTestCases()} {test_type.lower()} test(s)...")
    print("-" * 50)
    
    runner = ComprehensiveTestRunner(
        verbosity=verbosity,
        failfast=failfast,
        buffer=True
    )
    
    start_time = time.time()
    result = runner.run(suite)
    end_time = time.time()
    
    print(f"\n{test_type} tests completed in {end_time - start_time:.2f}s")
    
    return result


def main():
    """Main comprehensive test runner"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Run comprehensive MRUpdater tests')
    parser.add_argument(
        '--unit', '-u',
        action='store_true',
        help='Run unit tests only'
    )
    parser.add_argument(
        '--integration', '-i',
        action='store_true',
        help='Run integration tests only'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Verbose output'
    )
    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Quiet output (errors only)'
    )
    parser.add_argument(
        '--failfast', '-f',
        action='store_true',
        help='Stop on first failure'
    )
    parser.add_argument(
        '--check-env',
        action='store_true',
        help='Check test environment only'
    )
    
    args = parser.parse_args()
    
    # Set verbosity level
    if args.quiet:
        verbosity = 0
    elif args.verbose:
        verbosity = 2
    else:
        verbosity = 1
        
    print("MRUpdater Comprehensive Test Runner")
    print("="*50)
    
    # Check environment
    deps = check_test_environment()
    
    if args.check_env:
        return 0
        
    print()
    
    # Determine which tests to run
    if args.unit and args.integration:
        print("Running both unit and integration tests...")
        suite = discover_all_tests()
        test_type = "All"
    elif args.unit:
        print("Running unit tests only...")
        suite = discover_unit_tests()
        test_type = "Unit"
    elif args.integration:
        print("Running integration tests only...")
        suite = discover_integration_tests()
        test_type = "Integration"
    else:
        print("Running all tests...")
        suite = discover_all_tests()
        test_type = "All"
    
    # Run tests
    result = run_test_suite(suite, test_type, verbosity, args.failfast)
    
    if result is None:
        return 1
        
    # Print comprehensive summary
    success = print_comprehensive_summary(result, test_type)
    
    # Additional recommendations
    if not success:
        print("\n" + "="*70)
        print("RECOMMENDATIONS:")
        print("="*70)
        
        if result.failures:
            print("• Fix test failures by reviewing the error messages above")
        if result.errors:
            print("• Fix test errors by checking for missing dependencies or imports")
        if not deps['PySide6']:
            print("• Install PySide6 for GUI tests: pip install PySide6")
            
        print("• Run individual test modules for more detailed debugging:")
        print("  python -m pytest tests/test_specific_module.py -v")
        print("• Use --failfast to stop on first failure for faster debugging")
        
    print("="*70)
    
    # Return appropriate exit code
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
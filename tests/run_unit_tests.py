#!/usr/bin/env python3
"""
Unit test runner for MRUpdater.
Discovers and runs all unit tests with detailed reporting.
"""

import sys
import unittest
import logging
from pathlib import Path
from io import StringIO

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Configure logging for tests
logging.basicConfig(
    level=logging.WARNING,  # Reduce noise during tests
    format='%(name)s - %(levelname)s - %(message)s'
)

class ColoredTextTestResult(unittest.TextTestResult):
    """Custom test result class with colored output"""
    
    def __init__(self, stream, descriptions, verbosity):
        super().__init__(stream, descriptions, verbosity)
        self.success_count = 0
        
    def addSuccess(self, test):
        super().addSuccess(test)
        self.success_count += 1
        if self.verbosity > 1:
            self.stream.write("✓ ")
            self.stream.writeln(self.getDescription(test))
            
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


class ColoredTextTestRunner(unittest.TextTestRunner):
    """Custom test runner with colored output"""
    
    resultclass = ColoredTextTestResult
    
    def _makeResult(self):
        return self.resultclass(self.stream, self.descriptions, self.verbosity)


def discover_tests():
    """Discover all test modules"""
    test_dir = Path(__file__).parent
    loader = unittest.TestLoader()
    
    # Discover tests in the tests directory
    suite = loader.discover(
        start_dir=str(test_dir),
        pattern='test_*.py',
        top_level_dir=str(test_dir.parent)
    )
    
    return suite


def run_specific_test_module(module_name):
    """Run tests from a specific module"""
    loader = unittest.TestLoader()
    
    try:
        suite = loader.loadTestsFromName(f'tests.{module_name}')
        return suite
    except ImportError as e:
        print(f"Error loading test module '{module_name}': {e}")
        return None


def print_test_summary(result):
    """Print a detailed test summary"""
    total_tests = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    skipped = len(result.skipped)
    successes = result.success_count
    
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"Total tests run: {total_tests}")
    print(f"Successes: {successes} ✓")
    print(f"Failures: {failures} ✗")
    print(f"Errors: {errors} ✗")
    print(f"Skipped: {skipped} ⚠")
    
    if failures > 0:
        print(f"\nFAILURES ({failures}):")
        for test, traceback in result.failures:
            print(f"  - {test}")
            
    if errors > 0:
        print(f"\nERRORS ({errors}):")
        for test, traceback in result.errors:
            print(f"  - {test}")
            
    success_rate = (successes / total_tests * 100) if total_tests > 0 else 0
    print(f"\nSuccess rate: {success_rate:.1f}%")
    
    if success_rate == 100:
        print("🎉 All tests passed!")
    elif success_rate >= 80:
        print("✅ Most tests passed")
    else:
        print("❌ Many tests failed - review errors above")


def main():
    """Main test runner"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Run MRUpdater unit tests')
    parser.add_argument(
        '--module', '-m',
        help='Run tests from specific module (e.g., test_cartridge_operations)'
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
    
    args = parser.parse_args()
    
    # Set verbosity level
    if args.quiet:
        verbosity = 0
    elif args.verbose:
        verbosity = 2
    else:
        verbosity = 1
        
    print("MRUpdater Unit Test Runner")
    print("="*40)
    
    # Load tests
    if args.module:
        print(f"Running tests from module: {args.module}")
        suite = run_specific_test_module(args.module)
        if suite is None:
            return 1
    else:
        print("Discovering all unit tests...")
        suite = discover_tests()
        
    if suite.countTestCases() == 0:
        print("No tests found!")
        return 1
        
    print(f"Found {suite.countTestCases()} test(s)")
    print("-" * 40)
    
    # Run tests
    runner = ColoredTextTestRunner(
        verbosity=verbosity,
        failfast=args.failfast,
        buffer=True  # Capture stdout/stderr during tests
    )
    
    result = runner.run(suite)
    
    # Print summary
    print_test_summary(result)
    
    # Return appropriate exit code
    if result.wasSuccessful():
        return 0
    else:
        return 1


if __name__ == '__main__':
    sys.exit(main())
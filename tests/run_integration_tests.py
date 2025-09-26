#!/usr/bin/env python3
"""
Integration test runner for MRUpdater.
Runs integration tests with mock hardware and GUI tests.
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

class IntegrationTestResult(unittest.TextTestResult):
    """Custom test result class for integration tests"""
    
    def __init__(self, stream, descriptions, verbosity):
        super().__init__(stream, descriptions, verbosity)
        self.success_count = 0
        self.slow_tests = []
        
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


class IntegrationTestRunner(unittest.TextTestRunner):
    """Custom test runner for integration tests"""
    
    resultclass = IntegrationTestResult
    
    def _makeResult(self):
        return self.resultclass(self.stream, self.descriptions, self.verbosity)


def discover_integration_tests():
    """Discover integration test modules"""
    test_dir = Path(__file__).parent
    loader = unittest.TestLoader()
    
    # Discover integration tests
    integration_patterns = [
        'test_integration_*.py',
        'test_gui_*.py'
    ]
    
    suite = unittest.TestSuite()
    
    for pattern in integration_patterns:
        pattern_suite = loader.discover(
            start_dir=str(test_dir),
            pattern=pattern,
            top_level_dir=str(test_dir.parent)
        )
        suite.addTest(pattern_suite)
    
    return suite


def run_workflow_tests():
    """Run workflow integration tests"""
    loader = unittest.TestLoader()
    
    try:
        suite = loader.loadTestsFromName('tests.test_integration_workflows')
        return suite
    except ImportError as e:
        print(f"Error loading workflow tests: {e}")
        return unittest.TestSuite()


def run_gui_tests():
    """Run GUI integration tests"""
    loader = unittest.TestLoader()
    
    try:
        suite = loader.loadTestsFromName('tests.test_gui_integration')
        return suite
    except ImportError as e:
        print(f"Error loading GUI tests: {e}")
        return unittest.TestSuite()


def check_test_dependencies():
    """Check if test dependencies are available"""
    dependencies = {
        'PySide6': False,
        'unittest.mock': True,  # Part of standard library
    }
    
    try:
        import PySide6
        dependencies['PySide6'] = True
    except ImportError:
        pass
        
    return dependencies


def print_integration_test_summary(result):
    """Print detailed integration test summary"""
    total_tests = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    skipped = len(result.skipped)
    successes = result.success_count
    
    print("\n" + "="*60)
    print("INTEGRATION TEST SUMMARY")
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
            if len(traceback.split('\n')) > 10:
                # Show only last few lines for long tracebacks
                lines = traceback.split('\n')
                print(f"    ... (truncated)")
                print('\n'.join(f"    {line}" for line in lines[-3:]))
            else:
                print(f"    {traceback}")
            
    if errors > 0:
        print(f"\nERRORS ({errors}):")
        for test, traceback in result.errors:
            print(f"  - {test}")
            if len(traceback.split('\n')) > 10:
                lines = traceback.split('\n')
                print(f"    ... (truncated)")
                print('\n'.join(f"    {line}" for line in lines[-3:]))
            else:
                print(f"    {traceback}")
                
    if skipped > 0:
        print(f"\nSKIPPED ({skipped}):")
        for test, reason in result.skipped:
            print(f"  - {test}: {reason}")
            
    success_rate = (successes / total_tests * 100) if total_tests > 0 else 0
    print(f"\nSuccess rate: {success_rate:.1f}%")
    
    if success_rate == 100:
        print("🎉 All integration tests passed!")
    elif success_rate >= 80:
        print("✅ Most integration tests passed")
    else:
        print("❌ Many integration tests failed - review errors above")


def main():
    """Main integration test runner"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Run MRUpdater integration tests')
    parser.add_argument(
        '--workflows', '-w',
        action='store_true',
        help='Run workflow integration tests only'
    )
    parser.add_argument(
        '--gui', '-g',
        action='store_true',
        help='Run GUI integration tests only'
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
        
    print("MRUpdater Integration Test Runner")
    print("="*50)
    
    # Check dependencies
    deps = check_test_dependencies()
    print("Test Dependencies:")
    for dep, available in deps.items():
        status = "✓" if available else "✗"
        print(f"  {status} {dep}")
    print()
    
    # Load tests based on arguments
    if args.workflows:
        print("Running workflow integration tests...")
        suite = run_workflow_tests()
    elif args.gui:
        print("Running GUI integration tests...")
        suite = run_gui_tests()
    else:
        print("Discovering all integration tests...")
        suite = discover_integration_tests()
        
    if suite.countTestCases() == 0:
        print("No integration tests found!")
        return 1
        
    print(f"Found {suite.countTestCases()} integration test(s)")
    print("-" * 50)
    
    # Run tests
    runner = IntegrationTestRunner(
        verbosity=verbosity,
        failfast=args.failfast,
        buffer=True  # Capture stdout/stderr during tests
    )
    
    result = runner.run(suite)
    
    # Print summary
    print_integration_test_summary(result)
    
    # Return appropriate exit code
    if result.wasSuccessful():
        return 0
    else:
        return 1


if __name__ == '__main__':
    sys.exit(main())
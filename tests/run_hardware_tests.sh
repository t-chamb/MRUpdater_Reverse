#!/bin/bash
# Hardware testing script for MRUpdater
# Runs comprehensive hardware validation tests with real Chromatic devices

set -e  # Exit on any error

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
PYTHON_ENV="$PROJECT_ROOT/venv"
TEST_RESULTS_DIR="$PROJECT_ROOT/test_results"
LOG_FILE="$TEST_RESULTS_DIR/hardware_test_$(date +%Y%m%d_%H%M%S).log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1" | tee -a "$LOG_FILE"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOG_FILE"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
}

# Setup test environment
setup_test_environment() {
    log_info "Setting up hardware test environment..."
    
    # Create test results directory
    mkdir -p "$TEST_RESULTS_DIR"
    
    # Activate Python environment
    if [ -d "$PYTHON_ENV" ]; then
        source "$PYTHON_ENV/bin/activate"
        log_info "Activated Python virtual environment"
    else
        log_warning "Python virtual environment not found at $PYTHON_ENV"
        log_info "Using system Python"
    fi
    
    # Check Python dependencies
    python3 -c "import sys; print(f'Python version: {sys.version}')" | tee -a "$LOG_FILE"
    
    # Install test dependencies if needed
    if ! python3 -c "import pytest" 2>/dev/null; then
        log_info "Installing pytest..."
        pip install pytest
    fi
    
    log_success "Test environment setup completed"
}

# Check hardware prerequisites
check_hardware_prerequisites() {
    log_info "Checking hardware prerequisites..."
    
    # Check for USB devices
    if command -v system_profiler &> /dev/null; then
        log_info "Scanning for USB devices..."
        system_profiler SPUSBDataType | grep -A 10 -B 5 "Chromatic\|0x374E" | tee -a "$LOG_FILE" || {
            log_warning "No Chromatic devices detected in USB scan"
        }
    fi
    
    # Check USB permissions
    if [ -d "/dev" ]; then
        usb_devices=$(ls /dev/cu.usbmodem* 2>/dev/null | wc -l)
        log_info "Found $usb_devices USB modem devices"
    fi
    
    # Check network connectivity for firmware tests
    if ping -c 1 modretro.com &>/dev/null; then
        log_success "Network connectivity to ModRetro servers verified"
    else
        log_warning "Cannot reach ModRetro servers - firmware tests may fail"
    fi
    
    log_success "Hardware prerequisites check completed"
}

# Run device detection tests
run_device_tests() {
    log_info "Running device detection and communication tests..."
    
    python3 "$SCRIPT_DIR/hardware_validation.py" \
        --device-test \
        --verbose \
        2>&1 | tee -a "$LOG_FILE"
    
    local exit_code=${PIPESTATUS[0]}
    
    if [ $exit_code -eq 0 ]; then
        log_success "Device tests completed successfully"
    else
        log_error "Device tests failed with exit code $exit_code"
        return $exit_code
    fi
}

# Run firmware tests
run_firmware_tests() {
    local firmware_version="${1:-latest}"
    
    log_info "Running firmware download and validation tests (version: $firmware_version)..."
    
    python3 "$SCRIPT_DIR/hardware_validation.py" \
        --firmware-test \
        --firmware-version "$firmware_version" \
        --verbose \
        2>&1 | tee -a "$LOG_FILE"
    
    local exit_code=${PIPESTATUS[0]}
    
    if [ $exit_code -eq 0 ]; then
        log_success "Firmware tests completed successfully"
    else
        log_error "Firmware tests failed with exit code $exit_code"
        return $exit_code
    fi
}

# Run cartridge tests
run_cartridge_tests() {
    local test_rom_path="$1"
    
    log_info "Running cartridge operation tests..."
    
    if [ -n "$test_rom_path" ] && [ -f "$test_rom_path" ]; then
        log_info "Using test ROM: $test_rom_path"
        python3 "$SCRIPT_DIR/hardware_validation.py" \
            --cartridge-test \
            --rom-path "$test_rom_path" \
            --verbose \
            2>&1 | tee -a "$LOG_FILE"
    else
        log_info "No test ROM specified - running read-only cartridge tests"
        python3 "$SCRIPT_DIR/hardware_validation.py" \
            --cartridge-test \
            --verbose \
            2>&1 | tee -a "$LOG_FILE"
    fi
    
    local exit_code=${PIPESTATUS[0]}
    
    if [ $exit_code -eq 0 ]; then
        log_success "Cartridge tests completed successfully"
    else
        log_error "Cartridge tests failed with exit code $exit_code"
        return $exit_code
    fi
}

# Run full test suite
run_full_test_suite() {
    local firmware_version="${1:-latest}"
    local test_rom_path="$2"
    
    log_info "Running complete hardware validation test suite..."
    
    local cmd="python3 $SCRIPT_DIR/hardware_validation.py --full-suite --firmware-version $firmware_version --verbose"
    
    if [ -n "$test_rom_path" ] && [ -f "$test_rom_path" ]; then
        cmd="$cmd --rom-path $test_rom_path"
    fi
    
    eval "$cmd" 2>&1 | tee -a "$LOG_FILE"
    
    local exit_code=${PIPESTATUS[0]}
    
    if [ $exit_code -eq 0 ]; then
        log_success "Full test suite completed successfully"
    else
        log_error "Full test suite failed with exit code $exit_code"
        return $exit_code
    fi
}

# Interactive test selection
interactive_test_selection() {
    echo ""
    echo "=== MRUpdater Hardware Test Suite ==="
    echo ""
    echo "Available test options:"
    echo "1. Device Tests Only"
    echo "2. Firmware Tests Only"
    echo "3. Cartridge Tests Only"
    echo "4. Full Test Suite"
    echo "5. Custom Test Selection"
    echo "6. Exit"
    echo ""
    
    read -p "Select test option (1-6): " choice
    
    case $choice in
        1)
            run_device_tests
            ;;
        2)
            read -p "Enter firmware version (default: latest): " fw_version
            run_firmware_tests "${fw_version:-latest}"
            ;;
        3)
            read -p "Enter test ROM path (optional): " rom_path
            run_cartridge_tests "$rom_path"
            ;;
        4)
            read -p "Enter firmware version (default: latest): " fw_version
            read -p "Enter test ROM path (optional): " rom_path
            run_full_test_suite "${fw_version:-latest}" "$rom_path"
            ;;
        5)
            custom_test_selection
            ;;
        6)
            log_info "Exiting test suite"
            exit 0
            ;;
        *)
            log_error "Invalid selection: $choice"
            interactive_test_selection
            ;;
    esac
}

# Custom test selection
custom_test_selection() {
    echo ""
    echo "=== Custom Test Selection ==="
    echo ""
    
    # Device tests
    read -p "Run device tests? (y/n): " run_device
    
    # Firmware tests
    read -p "Run firmware tests? (y/n): " run_firmware
    if [[ "$run_firmware" =~ ^[Yy]$ ]]; then
        read -p "Enter firmware version (default: latest): " fw_version
        fw_version="${fw_version:-latest}"
    fi
    
    # Cartridge tests
    read -p "Run cartridge tests? (y/n): " run_cartridge
    if [[ "$run_cartridge" =~ ^[Yy]$ ]]; then
        read -p "Enter test ROM path (optional): " rom_path
    fi
    
    # Run selected tests
    local test_failed=false
    
    if [[ "$run_device" =~ ^[Yy]$ ]]; then
        if ! run_device_tests; then
            test_failed=true
        fi
    fi
    
    if [[ "$run_firmware" =~ ^[Yy]$ ]]; then
        if ! run_firmware_tests "$fw_version"; then
            test_failed=true
        fi
    fi
    
    if [[ "$run_cartridge" =~ ^[Yy]$ ]]; then
        if ! run_cartridge_tests "$rom_path"; then
            test_failed=true
        fi
    fi
    
    if [ "$test_failed" = true ]; then
        log_error "One or more tests failed"
        return 1
    else
        log_success "All selected tests completed successfully"
        return 0
    fi
}

# Generate test report
generate_test_report() {
    log_info "Generating test report..."
    
    local report_file="$TEST_RESULTS_DIR/hardware_test_report_$(date +%Y%m%d_%H%M%S).html"
    
    cat > "$report_file" << EOF
<!DOCTYPE html>
<html>
<head>
    <title>MRUpdater Hardware Test Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .header { background-color: #f0f0f0; padding: 20px; border-radius: 5px; }
        .test-section { margin: 20px 0; }
        .pass { color: green; }
        .fail { color: red; }
        .warning { color: orange; }
        .log { background-color: #f8f8f8; padding: 10px; font-family: monospace; white-space: pre-wrap; }
    </style>
</head>
<body>
    <div class="header">
        <h1>MRUpdater Hardware Test Report</h1>
        <p>Generated: $(date)</p>
        <p>Test Log: $LOG_FILE</p>
    </div>
    
    <div class="test-section">
        <h2>Test Results</h2>
        <p>See detailed results in the JSON files in the test_results directory.</p>
    </div>
    
    <div class="test-section">
        <h2>Test Log</h2>
        <div class="log">
$(cat "$LOG_FILE" | sed 's/&/\&amp;/g; s/</\&lt;/g; s/>/\&gt;/g')
        </div>
    </div>
</body>
</html>
EOF
    
    log_success "Test report generated: $report_file"
}

# Cleanup test environment
cleanup_test_environment() {
    log_info "Cleaning up test environment..."
    
    # Archive old test results
    if [ -d "$TEST_RESULTS_DIR" ]; then
        local archive_dir="$TEST_RESULTS_DIR/archive"
        mkdir -p "$archive_dir"
        
        # Move files older than 7 days to archive
        find "$TEST_RESULTS_DIR" -name "*.json" -mtime +7 -exec mv {} "$archive_dir/" \; 2>/dev/null || true
        find "$TEST_RESULTS_DIR" -name "*.log" -mtime +7 -exec mv {} "$archive_dir/" \; 2>/dev/null || true
    fi
    
    log_success "Test environment cleanup completed"
}

# Print usage information
print_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --device              Run device tests only"
    echo "  --firmware [VERSION]  Run firmware tests (default version: latest)"
    echo "  --cartridge [ROM]     Run cartridge tests (optional ROM path)"
    echo "  --full [VERSION] [ROM] Run full test suite"
    echo "  --interactive         Interactive test selection"
    echo "  --help, -h            Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 --device"
    echo "  $0 --firmware latest"
    echo "  $0 --cartridge /path/to/test.gb"
    echo "  $0 --full latest /path/to/test.gb"
    echo "  $0 --interactive"
    echo ""
    echo "Environment Variables:"
    echo "  MRUPDATER_DEBUG=1     Enable debug logging"
    echo "  MRUPDATER_VERBOSE=1   Enable verbose output"
}

# Main execution
main() {
    log_info "Starting MRUpdater hardware test suite..."
    log_info "Log file: $LOG_FILE"
    
    # Setup environment
    setup_test_environment
    check_hardware_prerequisites
    
    # Parse command line arguments
    case "${1:-}" in
        --device)
            run_device_tests
            ;;
        --firmware)
            run_firmware_tests "${2:-latest}"
            ;;
        --cartridge)
            run_cartridge_tests "$2"
            ;;
        --full)
            run_full_test_suite "${2:-latest}" "$3"
            ;;
        --interactive)
            interactive_test_selection
            ;;
        --help|-h)
            print_usage
            exit 0
            ;;
        "")
            # No arguments - run interactive mode
            interactive_test_selection
            ;;
        *)
            log_error "Unknown option: $1"
            print_usage
            exit 1
            ;;
    esac
    
    local exit_code=$?
    
    # Generate report and cleanup
    generate_test_report
    cleanup_test_environment
    
    if [ $exit_code -eq 0 ]; then
        log_success "Hardware test suite completed successfully"
    else
        log_error "Hardware test suite completed with errors"
    fi
    
    exit $exit_code
}

# Handle script interruption
trap 'log_warning "Test suite interrupted by user"; cleanup_test_environment; exit 130' INT TERM

# Run main function
main "$@"
#!/bin/bash
# Build script for MRUpdater macOS application
# Creates a signed and notarized .app bundle and .dmg installer

set -e  # Exit on any error

# Configuration
APP_NAME="MRUpdater"
BUNDLE_ID="com.modretro.mrupdater"
DEVELOPER_ID="Developer ID Application: ModRetro (XXXXXXXXXX)"  # Replace with actual ID
INSTALLER_ID="Developer ID Installer: ModRetro (XXXXXXXXXX)"    # Replace with actual ID
NOTARIZATION_PROFILE="modretro-notarization"  # Replace with actual profile name

# Paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BUILD_DIR="$PROJECT_ROOT/build"
DIST_DIR="$PROJECT_ROOT/dist"
SPEC_FILE="$PROJECT_ROOT/build_config/pyinstaller_macos.spec"
DMG_DIR="$BUILD_DIR/dmg"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running on macOS
check_macos() {
    if [[ "$OSTYPE" != "darwin"* ]]; then
        log_error "This script must be run on macOS"
        exit 1
    fi
}

# Check dependencies
check_dependencies() {
    log_info "Checking build dependencies..."
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 is required but not installed"
        exit 1
    fi
    
    # Check PyInstaller
    if ! python3 -c "import PyInstaller" 2>/dev/null; then
        log_error "PyInstaller is required but not installed"
        log_info "Install with: pip3 install pyinstaller"
        exit 1
    fi
    
    # Check create-dmg (optional)
    if ! command -v create-dmg &> /dev/null; then
        log_warning "create-dmg not found. Install with: brew install create-dmg"
        log_warning "DMG creation will be skipped"
    fi
    
    # Check code signing tools
    if ! command -v codesign &> /dev/null; then
        log_warning "codesign not found. Code signing will be skipped"
    fi
    
    if ! command -v xcrun &> /dev/null; then
        log_warning "xcrun not found. Notarization will be skipped"
    fi
    
    log_success "Dependencies check completed"
}

# Clean previous builds
clean_build() {
    log_info "Cleaning previous builds..."
    
    rm -rf "$BUILD_DIR"
    rm -rf "$DIST_DIR"
    
    # Clean Python cache
    find "$PROJECT_ROOT" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
    find "$PROJECT_ROOT" -name "*.pyc" -delete 2>/dev/null || true
    
    log_success "Build directories cleaned"
}

# Install/update dependencies
install_dependencies() {
    log_info "Installing/updating Python dependencies..."
    
    cd "$PROJECT_ROOT"
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install requirements
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
    fi
    
    # Install PyInstaller if not present
    pip install pyinstaller
    
    log_success "Dependencies installed"
}

# Build application with PyInstaller
build_app() {
    log_info "Building application with PyInstaller..."
    
    cd "$PROJECT_ROOT"
    source venv/bin/activate
    
    # Run PyInstaller
    pyinstaller --clean --noconfirm "$SPEC_FILE"
    
    if [ ! -d "$DIST_DIR/$APP_NAME.app" ]; then
        log_error "PyInstaller build failed - app bundle not found"
        exit 1
    fi
    
    log_success "Application built successfully"
}

# Sign the application
sign_app() {
    local app_path="$DIST_DIR/$APP_NAME.app"
    
    if ! command -v codesign &> /dev/null; then
        log_warning "Skipping code signing - codesign not available"
        return 0
    fi
    
    if [ -z "$DEVELOPER_ID" ] || [[ "$DEVELOPER_ID" == *"XXXXXXXXXX"* ]]; then
        log_warning "Skipping code signing - Developer ID not configured"
        return 0
    fi
    
    log_info "Signing application..."
    
    # Sign all binaries and frameworks first
    find "$app_path" -type f \( -name "*.dylib" -o -name "*.so" -o -perm +111 \) -exec codesign --force --verify --verbose --sign "$DEVELOPER_ID" --options runtime {} \;
    
    # Sign the main app bundle
    codesign --force --verify --verbose --sign "$DEVELOPER_ID" --options runtime "$app_path"
    
    # Verify signature
    codesign --verify --deep --strict --verbose=2 "$app_path"
    
    log_success "Application signed successfully"
}

# Create DMG installer
create_dmg() {
    local app_path="$DIST_DIR/$APP_NAME.app"
    local dmg_path="$DIST_DIR/$APP_NAME.dmg"
    
    if ! command -v create-dmg &> /dev/null; then
        log_warning "Skipping DMG creation - create-dmg not available"
        return 0
    fi
    
    log_info "Creating DMG installer..."
    
    # Create DMG staging directory
    mkdir -p "$DMG_DIR"
    
    # Copy app to staging directory
    cp -R "$app_path" "$DMG_DIR/"
    
    # Create Applications symlink
    ln -sf /Applications "$DMG_DIR/Applications"
    
    # Create DMG
    create-dmg \
        --volname "$APP_NAME" \
        --volicon "$PROJECT_ROOT/resources/volume_icon.icns" \
        --window-pos 200 120 \
        --window-size 800 400 \
        --icon-size 100 \
        --icon "$APP_NAME.app" 200 190 \
        --hide-extension "$APP_NAME.app" \
        --app-drop-link 600 185 \
        --background "$PROJECT_ROOT/resources/dmg_background.png" \
        "$dmg_path" \
        "$DMG_DIR" || {
        
        # Fallback to simple DMG creation if create-dmg fails
        log_warning "create-dmg failed, creating simple DMG..."
        hdiutil create -volname "$APP_NAME" -srcfolder "$DMG_DIR" -ov -format UDZO "$dmg_path"
    }
    
    # Clean up staging directory
    rm -rf "$DMG_DIR"
    
    if [ -f "$dmg_path" ]; then
        log_success "DMG created: $dmg_path"
    else
        log_error "DMG creation failed"
        return 1
    fi
}

# Sign DMG
sign_dmg() {
    local dmg_path="$DIST_DIR/$APP_NAME.dmg"
    
    if ! command -v codesign &> /dev/null; then
        log_warning "Skipping DMG signing - codesign not available"
        return 0
    fi
    
    if [ -z "$INSTALLER_ID" ] || [[ "$INSTALLER_ID" == *"XXXXXXXXXX"* ]]; then
        log_warning "Skipping DMG signing - Installer ID not configured"
        return 0
    fi
    
    if [ ! -f "$dmg_path" ]; then
        log_warning "Skipping DMG signing - DMG not found"
        return 0
    fi
    
    log_info "Signing DMG..."
    
    codesign --force --verify --verbose --sign "$INSTALLER_ID" "$dmg_path"
    
    log_success "DMG signed successfully"
}

# Notarize application
notarize_app() {
    local app_path="$DIST_DIR/$APP_NAME.app"
    
    if ! command -v xcrun &> /dev/null; then
        log_warning "Skipping notarization - xcrun not available"
        return 0
    fi
    
    if [ -z "$NOTARIZATION_PROFILE" ] || [[ "$NOTARIZATION_PROFILE" == *"modretro-notarization"* ]]; then
        log_warning "Skipping notarization - profile not configured"
        return 0
    fi
    
    log_info "Notarizing application..."
    
    # Create ZIP for notarization
    local zip_path="$DIST_DIR/$APP_NAME.zip"
    cd "$DIST_DIR"
    zip -r "$APP_NAME.zip" "$APP_NAME.app"
    
    # Submit for notarization
    local request_id=$(xcrun notarytool submit "$zip_path" --keychain-profile "$NOTARIZATION_PROFILE" --wait --output-format json | jq -r '.id')
    
    if [ "$request_id" != "null" ] && [ -n "$request_id" ]; then
        log_info "Notarization submitted with ID: $request_id"
        
        # Wait for notarization to complete
        xcrun notarytool wait "$request_id" --keychain-profile "$NOTARIZATION_PROFILE"
        
        # Staple the notarization
        xcrun stapler staple "$app_path"
        
        log_success "Application notarized successfully"
    else
        log_error "Notarization submission failed"
        return 1
    fi
    
    # Clean up ZIP
    rm -f "$zip_path"
}

# Verify final build
verify_build() {
    local app_path="$DIST_DIR/$APP_NAME.app"
    
    log_info "Verifying final build..."
    
    # Check app bundle structure
    if [ ! -d "$app_path" ]; then
        log_error "App bundle not found"
        return 1
    fi
    
    if [ ! -f "$app_path/Contents/MacOS/$APP_NAME" ]; then
        log_error "Main executable not found"
        return 1
    fi
    
    if [ ! -f "$app_path/Contents/Info.plist" ]; then
        log_error "Info.plist not found"
        return 1
    fi
    
    # Check code signature
    if command -v codesign &> /dev/null; then
        if codesign --verify --deep --strict "$app_path" 2>/dev/null; then
            log_success "Code signature verified"
        else
            log_warning "Code signature verification failed or app not signed"
        fi
    fi
    
    # Check notarization
    if command -v spctl &> /dev/null; then
        if spctl --assess --verbose "$app_path" 2>/dev/null; then
            log_success "Notarization verified"
        else
            log_warning "Notarization verification failed or app not notarized"
        fi
    fi
    
    # Get app size
    local app_size=$(du -sh "$app_path" | cut -f1)
    log_info "App bundle size: $app_size"
    
    if [ -f "$DIST_DIR/$APP_NAME.dmg" ]; then
        local dmg_size=$(du -sh "$DIST_DIR/$APP_NAME.dmg" | cut -f1)
        log_info "DMG size: $dmg_size"
    fi
    
    log_success "Build verification completed"
}

# Print build summary
print_summary() {
    log_info "Build Summary:"
    echo "=============="
    
    if [ -d "$DIST_DIR/$APP_NAME.app" ]; then
        echo "✓ App Bundle: $DIST_DIR/$APP_NAME.app"
    fi
    
    if [ -f "$DIST_DIR/$APP_NAME.dmg" ]; then
        echo "✓ DMG Installer: $DIST_DIR/$APP_NAME.dmg"
    fi
    
    echo ""
    log_success "Build completed successfully!"
    echo ""
    log_info "To install the application:"
    echo "1. Open the DMG file (if created)"
    echo "2. Drag $APP_NAME.app to Applications folder"
    echo "3. Run the application from Applications"
    echo ""
    log_info "For distribution:"
    echo "1. Upload the DMG to your distribution platform"
    echo "2. Provide installation instructions to users"
    echo "3. Consider creating a release on GitHub"
}

# Main build process
main() {
    log_info "Starting MRUpdater macOS build process..."
    
    check_macos
    check_dependencies
    clean_build
    install_dependencies
    build_app
    sign_app
    create_dmg
    sign_dmg
    notarize_app
    verify_build
    print_summary
}

# Handle script arguments
case "${1:-}" in
    --clean-only)
        clean_build
        ;;
    --no-sign)
        DEVELOPER_ID=""
        INSTALLER_ID=""
        main
        ;;
    --no-notarize)
        NOTARIZATION_PROFILE=""
        main
        ;;
    --help|-h)
        echo "Usage: $0 [OPTIONS]"
        echo ""
        echo "Options:"
        echo "  --clean-only    Only clean build directories"
        echo "  --no-sign       Skip code signing"
        echo "  --no-notarize   Skip notarization"
        echo "  --help, -h      Show this help message"
        echo ""
        echo "Environment Variables:"
        echo "  DEVELOPER_ID    Developer ID for code signing"
        echo "  INSTALLER_ID    Installer ID for DMG signing"
        echo "  NOTARIZATION_PROFILE  Keychain profile for notarization"
        ;;
    *)
        main
        ;;
esac
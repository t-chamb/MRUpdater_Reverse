#!/bin/bash
# Code signing and notarization configuration for MRUpdater

# This file contains configuration for code signing and notarization
# Copy this to codesign_config_local.sh and fill in your actual values
# DO NOT commit the _local.sh file to version control

# =============================================================================
# CODE SIGNING CONFIGURATION
# =============================================================================

# Developer ID Application certificate for signing the app bundle
# Find this in Keychain Access under "My Certificates"
# Format: "Developer ID Application: Your Name (TEAM_ID)"
export DEVELOPER_ID_APPLICATION="Developer ID Application: ModRetro (XXXXXXXXXX)"

# Developer ID Installer certificate for signing the DMG
# Format: "Developer ID Installer: Your Name (TEAM_ID)"
export DEVELOPER_ID_INSTALLER="Developer ID Installer: ModRetro (XXXXXXXXXX)"

# Team ID from Apple Developer account
export TEAM_ID="XXXXXXXXXX"

# =============================================================================
# NOTARIZATION CONFIGURATION
# =============================================================================

# Apple ID for notarization (usually your developer account email)
export APPLE_ID="developer@modretro.com"

# App-specific password for notarization
# Generate this at appleid.apple.com under "App-Specific Passwords"
export APPLE_ID_PASSWORD="xxxx-xxxx-xxxx-xxxx"

# Keychain profile name for notarization credentials
# This will be created by the setup script
export NOTARIZATION_PROFILE="modretro-notarization"

# =============================================================================
# BUNDLE CONFIGURATION
# =============================================================================

# Application bundle identifier
export BUNDLE_ID="com.modretro.mrupdater"

# Application name
export APP_NAME="MRUpdater"

# =============================================================================
# ENTITLEMENTS
# =============================================================================

# Path to entitlements file
export ENTITLEMENTS_FILE="build_config/entitlements.plist"

# Hardened runtime options
export HARDENED_RUNTIME_OPTIONS="--options runtime"

# =============================================================================
# SIGNING OPTIONS
# =============================================================================

# Additional codesign options
export CODESIGN_OPTIONS="--force --verify --verbose --timestamp"

# Deep signing for all nested components
export DEEP_SIGN="--deep"

# Strict verification
export STRICT_VERIFY="--strict"

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

# Check if certificates are available
check_certificates() {
    echo "Checking for code signing certificates..."
    
    if security find-identity -v -p codesigning | grep -q "$DEVELOPER_ID_APPLICATION"; then
        echo "✓ Developer ID Application certificate found"
    else
        echo "✗ Developer ID Application certificate not found"
        echo "  Expected: $DEVELOPER_ID_APPLICATION"
        return 1
    fi
    
    if security find-identity -v -p codesigning | grep -q "$DEVELOPER_ID_INSTALLER"; then
        echo "✓ Developer ID Installer certificate found"
    else
        echo "✗ Developer ID Installer certificate not found"
        echo "  Expected: $DEVELOPER_ID_INSTALLER"
        return 1
    fi
    
    return 0
}

# Setup notarization keychain profile
setup_notarization() {
    echo "Setting up notarization keychain profile..."
    
    if [ -z "$APPLE_ID" ] || [ -z "$APPLE_ID_PASSWORD" ] || [ -z "$TEAM_ID" ]; then
        echo "✗ Notarization credentials not configured"
        return 1
    fi
    
    # Store credentials in keychain
    xcrun notarytool store-credentials "$NOTARIZATION_PROFILE" \
        --apple-id "$APPLE_ID" \
        --password "$APPLE_ID_PASSWORD" \
        --team-id "$TEAM_ID"
    
    if [ $? -eq 0 ]; then
        echo "✓ Notarization profile created successfully"
        return 0
    else
        echo "✗ Failed to create notarization profile"
        return 1
    fi
}

# Verify notarization setup
verify_notarization() {
    echo "Verifying notarization setup..."
    
    if xcrun notarytool history --keychain-profile "$NOTARIZATION_PROFILE" >/dev/null 2>&1; then
        echo "✓ Notarization profile is working"
        return 0
    else
        echo "✗ Notarization profile is not working"
        return 1
    fi
}

# Sign a single file or bundle
sign_item() {
    local item_path="$1"
    local identity="$2"
    local entitlements="$3"
    
    if [ ! -e "$item_path" ]; then
        echo "✗ Item not found: $item_path"
        return 1
    fi
    
    local sign_cmd="codesign $CODESIGN_OPTIONS $HARDENED_RUNTIME_OPTIONS --sign \"$identity\""
    
    if [ -n "$entitlements" ] && [ -f "$entitlements" ]; then
        sign_cmd="$sign_cmd --entitlements \"$entitlements\""
    fi
    
    sign_cmd="$sign_cmd \"$item_path\""
    
    echo "Signing: $item_path"
    eval $sign_cmd
    
    if [ $? -eq 0 ]; then
        echo "✓ Successfully signed: $item_path"
        return 0
    else
        echo "✗ Failed to sign: $item_path"
        return 1
    fi
}

# Verify signature of an item
verify_signature() {
    local item_path="$1"
    
    echo "Verifying signature: $item_path"
    
    codesign --verify $DEEP_SIGN $STRICT_VERIFY --verbose=2 "$item_path"
    
    if [ $? -eq 0 ]; then
        echo "✓ Signature verified: $item_path"
        return 0
    else
        echo "✗ Signature verification failed: $item_path"
        return 1
    fi
}

# Submit item for notarization
submit_for_notarization() {
    local item_path="$1"
    local item_name="$(basename "$item_path")"
    
    echo "Submitting for notarization: $item_name"
    
    # Create ZIP for submission
    local zip_path="/tmp/${item_name}.zip"
    cd "$(dirname "$item_path")"
    zip -r "$zip_path" "$(basename "$item_path")"
    
    # Submit to notarization service
    local request_id=$(xcrun notarytool submit "$zip_path" \
        --keychain-profile "$NOTARIZATION_PROFILE" \
        --wait \
        --output-format json | jq -r '.id')
    
    # Clean up ZIP
    rm -f "$zip_path"
    
    if [ "$request_id" != "null" ] && [ -n "$request_id" ]; then
        echo "✓ Notarization submitted successfully: $request_id"
        
        # Wait for completion and staple
        echo "Waiting for notarization to complete..."
        xcrun notarytool wait "$request_id" --keychain-profile "$NOTARIZATION_PROFILE"
        
        if [ $? -eq 0 ]; then
            echo "✓ Notarization completed successfully"
            
            # Staple the notarization ticket
            xcrun stapler staple "$item_path"
            
            if [ $? -eq 0 ]; then
                echo "✓ Notarization ticket stapled successfully"
                return 0
            else
                echo "✗ Failed to staple notarization ticket"
                return 1
            fi
        else
            echo "✗ Notarization failed"
            return 1
        fi
    else
        echo "✗ Failed to submit for notarization"
        return 1
    fi
}

# Validate final distribution
validate_distribution() {
    local app_path="$1"
    
    echo "Validating distribution readiness..."
    
    # Check code signature
    if ! verify_signature "$app_path"; then
        return 1
    fi
    
    # Check notarization
    echo "Checking notarization status..."
    if spctl --assess --verbose "$app_path" 2>&1 | grep -q "accepted"; then
        echo "✓ Notarization validated"
    else
        echo "✗ Notarization validation failed"
        return 1
    fi
    
    # Check Gatekeeper
    echo "Checking Gatekeeper compatibility..."
    if spctl --assess --type execute --verbose "$app_path" 2>&1 | grep -q "accepted"; then
        echo "✓ Gatekeeper validation passed"
    else
        echo "✗ Gatekeeper validation failed"
        return 1
    fi
    
    echo "✓ Distribution validation completed successfully"
    return 0
}

# =============================================================================
# MAIN FUNCTIONS
# =============================================================================

# Setup development environment
setup_development() {
    echo "Setting up development environment for code signing..."
    
    if ! check_certificates; then
        echo "Please install the required certificates in Keychain Access"
        return 1
    fi
    
    if ! setup_notarization; then
        echo "Please configure notarization credentials"
        return 1
    fi
    
    if ! verify_notarization; then
        echo "Notarization setup verification failed"
        return 1
    fi
    
    echo "✓ Development environment setup completed"
    return 0
}

# Print configuration status
print_status() {
    echo "=== Code Signing Configuration Status ==="
    echo "Developer ID Application: $DEVELOPER_ID_APPLICATION"
    echo "Developer ID Installer: $DEVELOPER_ID_INSTALLER"
    echo "Team ID: $TEAM_ID"
    echo "Apple ID: $APPLE_ID"
    echo "Notarization Profile: $NOTARIZATION_PROFILE"
    echo "Bundle ID: $BUNDLE_ID"
    echo "App Name: $APP_NAME"
    echo ""
    
    check_certificates
    verify_notarization
}

# =============================================================================
# SCRIPT EXECUTION
# =============================================================================

# If script is run directly, show status
if [ "${BASH_SOURCE[0]}" == "${0}" ]; then
    case "${1:-status}" in
        setup)
            setup_development
            ;;
        status)
            print_status
            ;;
        check)
            check_certificates && verify_notarization
            ;;
        *)
            echo "Usage: $0 [setup|status|check]"
            echo ""
            echo "Commands:"
            echo "  setup   - Setup development environment"
            echo "  status  - Show configuration status"
            echo "  check   - Check certificates and notarization"
            ;;
    esac
fi
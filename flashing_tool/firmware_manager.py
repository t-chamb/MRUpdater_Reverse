# Firmware download, validation, and management for Chromatic devices
# Implements S3 firmware manifest parsing, download, and local caching

import os
import json
import yaml
import hashlib
import tempfile
import logging
from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any, List, Tuple
from pathlib import Path
import requests
from packaging import version

from .s3_wrapper import S3Wrapper, S3WrapperError
from .constants import APP_DATA_DIR
from .version_detector import FirmwareVersion

logger = logging.getLogger('mrupdater.firmware_manager')

@dataclass
class S3FirmwareInfo:
    """S3 firmware information from manifest"""
    version: str
    mcu_binary_key: str
    fpga_bitstream_key: str
    changelog_key: Optional[str] = None
    release_notes_key: Optional[str] = None
    checksum_mcu: Optional[str] = None
    checksum_fpga: Optional[str] = None
    file_size_mcu: Optional[int] = None
    file_size_fpga: Optional[int] = None
    release_date: Optional[str] = None
    is_preview: bool = False
    is_rollback: bool = False
    minimum_bootloader_version: Optional[str] = None

@dataclass
class ChromaticFirmwarePackage:
    """Complete firmware package for Chromatic device"""
    version: str
    mcu_binary_path: str
    fpga_bitstream_path: str
    changelog: Optional[str] = None
    release_notes: Optional[str] = None
    checksum_mcu: Optional[str] = None
    checksum_fpga: Optional[str] = None
    file_size_mcu: Optional[int] = None
    file_size_fpga: Optional[int] = None
    release_date: Optional[str] = None
    is_preview: bool = False
    is_rollback: bool = False
    minimum_bootloader_version: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ChromaticFirmwarePackage':
        """Create from dictionary"""
        return cls(**data)

@dataclass
class FirmwareManifest:
    """Firmware manifest containing all available versions"""
    latest_version: str
    preview_version: Optional[str] = None
    rollback_version: Optional[str] = None
    firmware_list: List[S3FirmwareInfo] = None
    manifest_version: str = "1.0"
    last_updated: Optional[str] = None
    
    def __post_init__(self):
        if self.firmware_list is None:
            self.firmware_list = []

class FirmwareValidationError(Exception):
    """Raised when firmware validation fails"""
    pass

class FirmwareDownloadError(Exception):
    """Raised when firmware download fails"""
    pass

class FirmwareManager:
    """
    Manages firmware download, validation, and caching for Chromatic devices.
    
    Handles S3 manifest parsing, firmware package downloads, integrity checking,
    and local caching with version management.
    """
    
    def __init__(self, s3_wrapper: Optional[S3Wrapper] = None):
        self.s3_wrapper = s3_wrapper or S3Wrapper(bucket='updates.modretro.com')
        self.logger = logging.getLogger('mrupdater.firmware_manager')
        
        # Set up local cache directory
        self.cache_dir = Path(APP_DATA_DIR) / 'firmware_cache'
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Cache file paths
        self.manifest_cache_path = self.cache_dir / 'manifest.yaml'
        self.firmware_cache_dir = self.cache_dir / 'packages'
        self.firmware_cache_dir.mkdir(exist_ok=True)
        
        self.logger.info(f"Firmware cache directory: {self.cache_dir}")
    
    def get_firmware_manifest(self, force_refresh: bool = False) -> Optional[FirmwareManifest]:
        """
        Get firmware manifest from S3 or local cache.
        
        Args:
            force_refresh: Force download from S3 even if cached version exists
            
        Returns:
            FirmwareManifest: Parsed manifest, or None if failed
        """
        try:
            manifest_data = None
            
            # Try to use cached manifest if not forcing refresh
            if not force_refresh and self.manifest_cache_path.exists():
                try:
                    with open(self.manifest_cache_path, 'r') as f:
                        manifest_data = yaml.safe_load(f)
                    self.logger.debug("Using cached firmware manifest")
                except Exception as e:
                    self.logger.warning(f"Failed to load cached manifest: {e}")
            
            # Download fresh manifest if needed
            if manifest_data is None:
                self.logger.info("Downloading firmware manifest from S3")
                manifest_content = self.s3_wrapper.read_manifest()
                manifest_data = yaml.safe_load(manifest_content)
                
                # Cache the manifest
                try:
                    with open(self.manifest_cache_path, 'w') as f:
                        yaml.dump(manifest_data, f)
                    self.logger.debug("Cached firmware manifest")
                except Exception as e:
                    self.logger.warning(f"Failed to cache manifest: {e}")
            
            # Parse manifest data
            manifest = self._parse_manifest(manifest_data)
            
            if manifest:
                self.logger.info(f"Loaded firmware manifest: {len(manifest.firmware_list)} versions available")
                self.logger.info(f"Latest version: {manifest.latest_version}")
                if manifest.preview_version:
                    self.logger.info(f"Preview version: {manifest.preview_version}")
            
            return manifest
            
        except S3WrapperError as e:
            self.logger.error(f"S3 error loading firmware manifest: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Error loading firmware manifest: {e}")
            return None
    
    def _parse_manifest(self, manifest_data: Dict[str, Any]) -> Optional[FirmwareManifest]:
        """
        Parse raw manifest data into FirmwareManifest object.
        
        Args:
            manifest_data: Raw manifest data from YAML
            
        Returns:
            FirmwareManifest: Parsed manifest, or None if parsing failed
        """
        try:
            # Extract basic manifest info
            latest_version = manifest_data.get('latest_version', '')
            preview_version = manifest_data.get('preview_version')
            rollback_version = manifest_data.get('rollback_version')
            manifest_version = manifest_data.get('manifest_version', '1.0')
            last_updated = manifest_data.get('last_updated')
            
            # Parse firmware list
            firmware_list = []
            firmware_data = manifest_data.get('firmware', [])
            
            for fw_data in firmware_data:
                try:
                    firmware_info = S3FirmwareInfo(
                        version=fw_data['version'],
                        mcu_binary_key=fw_data['mcu_binary'],
                        fpga_bitstream_key=fw_data['fpga_bitstream'],
                        changelog_key=fw_data.get('changelog'),
                        release_notes_key=fw_data.get('release_notes'),
                        checksum_mcu=fw_data.get('checksum_mcu'),
                        checksum_fpga=fw_data.get('checksum_fpga'),
                        file_size_mcu=fw_data.get('file_size_mcu'),
                        file_size_fpga=fw_data.get('file_size_fpga'),
                        release_date=fw_data.get('release_date'),
                        is_preview=fw_data.get('is_preview', False),
                        is_rollback=fw_data.get('is_rollback', False),
                        minimum_bootloader_version=fw_data.get('minimum_bootloader_version')
                    )
                    firmware_list.append(firmware_info)
                except KeyError as e:
                    self.logger.warning(f"Skipping invalid firmware entry: missing {e}")
                    continue
            
            manifest = FirmwareManifest(
                latest_version=latest_version,
                preview_version=preview_version,
                rollback_version=rollback_version,
                firmware_list=firmware_list,
                manifest_version=manifest_version,
                last_updated=last_updated
            )
            
            return manifest
            
        except Exception as e:
            self.logger.error(f"Error parsing firmware manifest: {e}")
            return None
    
    def get_firmware_info(self, version_str: str, 
                         manifest: Optional[FirmwareManifest] = None) -> Optional[S3FirmwareInfo]:
        """
        Get firmware information for a specific version.
        
        Args:
            version_str: Version string to find
            manifest: Firmware manifest (will be fetched if not provided)
            
        Returns:
            S3FirmwareInfo: Firmware info, or None if not found
        """
        if manifest is None:
            manifest = self.get_firmware_manifest()
            if not manifest:
                return None
        
        # Search for exact version match
        for firmware_info in manifest.firmware_list:
            if firmware_info.version == version_str:
                return firmware_info
        
        # Try version aliases
        if version_str == 'latest':
            return self.get_firmware_info(manifest.latest_version, manifest)
        elif version_str == 'preview' and manifest.preview_version:
            return self.get_firmware_info(manifest.preview_version, manifest)
        elif version_str == 'rollback' and manifest.rollback_version:
            return self.get_firmware_info(manifest.rollback_version, manifest)
        
        self.logger.warning(f"Firmware version '{version_str}' not found in manifest")
        return None
    
    def download_firmware(self, firmware_info: S3FirmwareInfo, 
                         progress_callback: Optional[callable] = None) -> Optional[ChromaticFirmwarePackage]:
        """
        Download firmware package from S3.
        
        Args:
            firmware_info: Firmware information from manifest
            progress_callback: Optional callback for progress updates
            
        Returns:
            ChromaticFirmwarePackage: Downloaded firmware package, or None if failed
        """
        try:
            self.logger.info(f"Downloading firmware version {firmware_info.version}")
            
            # Check if already cached
            cached_package = self._get_cached_firmware(firmware_info.version)
            if cached_package and self._validate_cached_firmware(cached_package, firmware_info):
                self.logger.info(f"Using cached firmware version {firmware_info.version}")
                return cached_package
            
            # Create version-specific cache directory
            version_cache_dir = self.firmware_cache_dir / firmware_info.version
            version_cache_dir.mkdir(exist_ok=True)
            
            # Download MCU binary
            if progress_callback:
                progress_callback("Downloading MCU firmware...")
            
            mcu_path = version_cache_dir / 'mcu_firmware.bin'
            self._download_file_with_validation(
                firmware_info.mcu_binary_key,
                mcu_path,
                firmware_info.checksum_mcu,
                firmware_info.file_size_mcu
            )
            
            # Download FPGA bitstream
            if progress_callback:
                progress_callback("Downloading FPGA bitstream...")
            
            fpga_path = version_cache_dir / 'fpga_bitstream.fs'
            self._download_file_with_validation(
                firmware_info.fpga_bitstream_key,
                fpga_path,
                firmware_info.checksum_fpga,
                firmware_info.file_size_fpga
            )
            
            # Download optional files
            changelog = None
            if firmware_info.changelog_key:
                try:
                    if progress_callback:
                        progress_callback("Downloading changelog...")
                    changelog = self.s3_wrapper.read_file(firmware_info.changelog_key)
                except Exception as e:
                    self.logger.warning(f"Failed to download changelog: {e}")
            
            release_notes = None
            if firmware_info.release_notes_key:
                try:
                    if progress_callback:
                        progress_callback("Downloading release notes...")
                    release_notes = self.s3_wrapper.read_file(firmware_info.release_notes_key)
                except Exception as e:
                    self.logger.warning(f"Failed to download release notes: {e}")
            
            # Create firmware package
            firmware_package = ChromaticFirmwarePackage(
                version=firmware_info.version,
                mcu_binary_path=str(mcu_path),
                fpga_bitstream_path=str(fpga_path),
                changelog=changelog,
                release_notes=release_notes,
                checksum_mcu=firmware_info.checksum_mcu,
                checksum_fpga=firmware_info.checksum_fpga,
                file_size_mcu=firmware_info.file_size_mcu,
                file_size_fpga=firmware_info.file_size_fpga,
                release_date=firmware_info.release_date,
                is_preview=firmware_info.is_preview,
                is_rollback=firmware_info.is_rollback,
                minimum_bootloader_version=firmware_info.minimum_bootloader_version
            )
            
            # Cache package metadata
            self._cache_firmware_metadata(firmware_package)
            
            if progress_callback:
                progress_callback("Download complete")
            
            self.logger.info(f"Successfully downloaded firmware version {firmware_info.version}")
            return firmware_package
            
        except Exception as e:
            self.logger.error(f"Error downloading firmware: {e}")
            raise FirmwareDownloadError(f"Failed to download firmware: {e}")
    
    def _download_file_with_validation(self, s3_key: str, local_path: Path, 
                                     expected_checksum: Optional[str] = None,
                                     expected_size: Optional[int] = None):
        """
        Download file from S3 with validation.
        
        Args:
            s3_key: S3 object key
            local_path: Local file path
            expected_checksum: Expected SHA256 checksum
            expected_size: Expected file size in bytes
        """
        try:
            # Download file
            downloaded_path = self.s3_wrapper.download_file(s3_key)
            
            # Validate file size
            if expected_size is not None:
                actual_size = os.path.getsize(downloaded_path)
                if actual_size != expected_size:
                    raise FirmwareValidationError(
                        f"File size mismatch: expected {expected_size}, got {actual_size}"
                    )
            
            # Validate checksum
            if expected_checksum:
                actual_checksum = self._calculate_file_checksum(downloaded_path)
                if actual_checksum != expected_checksum:
                    raise FirmwareValidationError(
                        f"Checksum mismatch: expected {expected_checksum}, got {actual_checksum}"
                    )
            
            # Move to final location
            os.rename(downloaded_path, local_path)
            
        except Exception as e:
            # Clean up on failure
            if os.path.exists(downloaded_path):
                os.remove(downloaded_path)
            raise
    
    def _calculate_file_checksum(self, file_path: str) -> str:
        """
        Calculate SHA256 checksum of file.
        
        Args:
            file_path: Path to file
            
        Returns:
            str: SHA256 checksum in hexadecimal
        """
        sha256_hash = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()
    
    def _get_cached_firmware(self, version_str: str) -> Optional[ChromaticFirmwarePackage]:
        """
        Get cached firmware package if available.
        
        Args:
            version_str: Firmware version
            
        Returns:
            ChromaticFirmwarePackage: Cached package, or None if not found
        """
        try:
            version_cache_dir = self.firmware_cache_dir / version_str
            metadata_path = version_cache_dir / 'package.json'
            
            if not metadata_path.exists():
                return None
            
            with open(metadata_path, 'r') as f:
                package_data = json.load(f)
            
            package = ChromaticFirmwarePackage.from_dict(package_data)
            
            # Verify files still exist
            if not os.path.exists(package.mcu_binary_path):
                return None
            if not os.path.exists(package.fpga_bitstream_path):
                return None
            
            return package
            
        except Exception as e:
            self.logger.debug(f"Failed to load cached firmware {version_str}: {e}")
            return None
    
    def _validate_cached_firmware(self, package: ChromaticFirmwarePackage, 
                                firmware_info: S3FirmwareInfo) -> bool:
        """
        Validate cached firmware package against manifest info.
        
        Args:
            package: Cached firmware package
            firmware_info: Firmware info from manifest
            
        Returns:
            bool: True if cached package is valid
        """
        try:
            # Check version match
            if package.version != firmware_info.version:
                return False
            
            # Validate MCU binary checksum if available
            if firmware_info.checksum_mcu:
                actual_checksum = self._calculate_file_checksum(package.mcu_binary_path)
                if actual_checksum != firmware_info.checksum_mcu:
                    self.logger.warning(f"MCU binary checksum mismatch for cached version {package.version}")
                    return False
            
            # Validate FPGA bitstream checksum if available
            if firmware_info.checksum_fpga:
                actual_checksum = self._calculate_file_checksum(package.fpga_bitstream_path)
                if actual_checksum != firmware_info.checksum_fpga:
                    self.logger.warning(f"FPGA bitstream checksum mismatch for cached version {package.version}")
                    return False
            
            return True
            
        except Exception as e:
            self.logger.warning(f"Error validating cached firmware: {e}")
            return False
    
    def _cache_firmware_metadata(self, package: ChromaticFirmwarePackage):
        """
        Cache firmware package metadata.
        
        Args:
            package: Firmware package to cache
        """
        try:
            version_cache_dir = self.firmware_cache_dir / package.version
            metadata_path = version_cache_dir / 'package.json'
            
            with open(metadata_path, 'w') as f:
                json.dump(package.to_dict(), f, indent=2)
            
        except Exception as e:
            self.logger.warning(f"Failed to cache firmware metadata: {e}")
    
    def list_cached_versions(self) -> List[str]:
        """
        List all cached firmware versions.
        
        Returns:
            List[str]: List of cached version strings
        """
        cached_versions = []
        
        try:
            for version_dir in self.firmware_cache_dir.iterdir():
                if version_dir.is_dir():
                    metadata_path = version_dir / 'package.json'
                    if metadata_path.exists():
                        cached_versions.append(version_dir.name)
        except Exception as e:
            self.logger.error(f"Error listing cached versions: {e}")
        
        return sorted(cached_versions, key=lambda v: version.parse(v) if self._is_valid_version(v) else v)
    
    def _is_valid_version(self, version_str: str) -> bool:
        """Check if version string is valid for sorting"""
        try:
            version.parse(version_str)
            return True
        except version.InvalidVersion:
            return False
    
    def clear_cache(self, version_str: Optional[str] = None):
        """
        Clear firmware cache.
        
        Args:
            version_str: Specific version to clear, or None to clear all
        """
        try:
            if version_str:
                # Clear specific version
                version_cache_dir = self.firmware_cache_dir / version_str
                if version_cache_dir.exists():
                    import shutil
                    shutil.rmtree(version_cache_dir)
                    self.logger.info(f"Cleared cache for firmware version {version_str}")
            else:
                # Clear all cached firmware
                import shutil
                if self.firmware_cache_dir.exists():
                    shutil.rmtree(self.firmware_cache_dir)
                    self.firmware_cache_dir.mkdir(exist_ok=True)
                
                # Clear manifest cache
                if self.manifest_cache_path.exists():
                    self.manifest_cache_path.unlink()
                
                self.logger.info("Cleared all firmware cache")
                
        except Exception as e:
            self.logger.error(f"Error clearing cache: {e}")
    
    def get_cache_size(self) -> int:
        """
        Get total size of firmware cache in bytes.
        
        Returns:
            int: Cache size in bytes
        """
        total_size = 0
        
        try:
            for root, dirs, files in os.walk(self.cache_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    if os.path.exists(file_path):
                        total_size += os.path.getsize(file_path)
        except Exception as e:
            self.logger.error(f"Error calculating cache size: {e}")
        
        return total_size
    
    def validate_firmware_package(self, package: ChromaticFirmwarePackage) -> bool:
        """
        Validate firmware package integrity.
        
        Args:
            package: Firmware package to validate
            
        Returns:
            bool: True if package is valid
        """
        try:
            # Check that files exist
            if not os.path.exists(package.mcu_binary_path):
                self.logger.error(f"MCU binary not found: {package.mcu_binary_path}")
                return False
            
            if not os.path.exists(package.fpga_bitstream_path):
                self.logger.error(f"FPGA bitstream not found: {package.fpga_bitstream_path}")
                return False
            
            # Validate checksums if available
            if package.checksum_mcu:
                actual_checksum = self._calculate_file_checksum(package.mcu_binary_path)
                if actual_checksum != package.checksum_mcu:
                    self.logger.error(f"MCU binary checksum validation failed")
                    return False
            
            if package.checksum_fpga:
                actual_checksum = self._calculate_file_checksum(package.fpga_bitstream_path)
                if actual_checksum != package.checksum_fpga:
                    self.logger.error(f"FPGA bitstream checksum validation failed")
                    return False
            
            # Validate file sizes if available
            if package.file_size_mcu:
                actual_size = os.path.getsize(package.mcu_binary_path)
                if actual_size != package.file_size_mcu:
                    self.logger.error(f"MCU binary size validation failed")
                    return False
            
            if package.file_size_fpga:
                actual_size = os.path.getsize(package.fpga_bitstream_path)
                if actual_size != package.file_size_fpga:
                    self.logger.error(f"FPGA bitstream size validation failed")
                    return False
            
            self.logger.info(f"Firmware package {package.version} validation successful")
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating firmware package: {e}")
            return False
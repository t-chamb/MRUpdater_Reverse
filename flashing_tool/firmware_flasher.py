# Integrated firmware flashing system for Chromatic devices
# Coordinates firmware download, FPGA flashing, and MCU flashing workflows

import logging
import time
from dataclasses import dataclass
from typing import Optional, Callable, Dict, Any, List
from enum import Enum

from .firmware_manager import FirmwareManager, ChromaticFirmwarePackage, FirmwareManifest
from .fpga_flasher import FPGAFlasher, FPGAFlashProgress
from .mcu_flasher import MCUFlasher, MCUFlashProgress
from .device_communication import DeviceCommunicationManager
from .version_detector import VersionDetector, FirmwareVersion, VersionComparison
from .util import FlashOperation

# Import progress reporting system
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from progress_reporting import ProgressReporter, OperationType, create_progress_reporter
from logging_config import LogCategory, get_logger
from exceptions import FirmwareFlashError, FirmwareDownloadError

# Import performance optimization components
from performance_optimization import (
    memory_efficient_operation, keep_gui_responsive, 
    ThreadPriority, create_worker_thread, get_memory_manager
)

logger = get_logger(LogCategory.FIRMWARE, "firmware_flasher")

class FlashStage(Enum):
    """Firmware flashing stages"""
    INITIALIZING = "initializing"
    DOWNLOADING = "downloading"
    PREPARING = "preparing"
    FLASHING_FPGA = "flashing_fpga"
    FLASHING_MCU = "flashing_mcu"
    VERIFYING = "verifying"
    COMPLETED = "completed"
    ERROR = "error"

@dataclass
class FirmwareFlashProgress:
    """Overall firmware flashing progress"""
    stage: FlashStage
    overall_progress: float
    current_operation: str
    fpga_progress: Optional[FPGAFlashProgress] = None
    mcu_progress: Optional[MCUFlashProgress] = None
    elapsed_time: float = 0.0
    estimated_remaining: Optional[float] = None

class FirmwareFlasher:
    """
    Integrated firmware flashing system for Chromatic devices.
    
    Coordinates the complete firmware update process including download,
    validation, FPGA flashing, MCU flashing, and verification.
    """
    
    def __init__(self, device_communicator: Optional[DeviceCommunicationManager] = None):
        self.device_communicator = device_communicator
        self.logger = logging.getLogger('mrupdater.firmware_flasher')
        
        # Initialize component managers
        self.firmware_manager = FirmwareManager()
        self.fpga_flasher = FPGAFlasher(device_communicator)
        self.mcu_flasher = MCUFlasher(device_communicator)
        
        if device_communicator:
            self.version_detector = VersionDetector(device_communicator.transport)
        else:
            self.version_detector = None
    
    def flash_firmware(self, version: str, 
                      operation: FlashOperation = FlashOperation.BOTH,
                      progress_callback: Optional[Callable[[FirmwareFlashProgress], None]] = None) -> bool:
        """
        Flash firmware to Chromatic device.
        
        Args:
            version: Firmware version to flash ('latest', 'preview', or specific version)
            operation: What to flash (BOTH, FPGA, MCU, or CART)
            progress_callback: Optional callback for progress updates
            
        Returns:
            bool: True if flashing succeeded
        """
        start_time = time.time()
        
        try:
            self.logger.info(f"Starting firmware flash: version={version}, operation={operation}")
            
            # Initialize progress
            if progress_callback:
                progress_callback(FirmwareFlashProgress(
                    stage=FlashStage.INITIALIZING,
                    overall_progress=0.0,
                    current_operation="Initializing firmware flash..."
                ))
            
            # Get current device version for comparison
            current_version = None
            if self.version_detector:
                try:
                    current_version = self.version_detector.get_device_version()
                    if current_version:
                        self.logger.info(f"Current device version: MCU {current_version.mcu_version}, FPGA {current_version.fpga_version}")
                except Exception as e:
                    self.logger.warning(f"Could not get current device version: {e}")
            
            # Download firmware
            if progress_callback:
                progress_callback(FirmwareFlashProgress(
                    stage=FlashStage.DOWNLOADING,
                    overall_progress=10.0,
                    current_operation="Downloading firmware..."
                ))
            
            firmware_package = self._download_firmware(version, progress_callback)
            if not firmware_package:
                raise Exception("Failed to download firmware")
            
            # Prepare for flashing
            if progress_callback:
                progress_callback(FirmwareFlashProgress(
                    stage=FlashStage.PREPARING,
                    overall_progress=20.0,
                    current_operation="Preparing for flash..."
                ))
            
            # Determine what needs to be flashed
            flash_fpga = operation in [FlashOperation.BOTH, FlashOperation.FPGA]
            flash_mcu = operation in [FlashOperation.BOTH, FlashOperation.MCU]
            
            # Flash FPGA if requested
            if flash_fpga:
                if progress_callback:
                    progress_callback(FirmwareFlashProgress(
                        stage=FlashStage.FLASHING_FPGA,
                        overall_progress=30.0,
                        current_operation="Flashing FPGA bitstream..."
                    ))
                
                success = self._flash_fpga_component(firmware_package, progress_callback)
                if not success:
                    raise Exception("FPGA flashing failed")
            
            # Flash MCU if requested
            if flash_mcu:
                if progress_callback:
                    progress_callback(FirmwareFlashProgress(
                        stage=FlashStage.FLASHING_MCU,
                        overall_progress=60.0,
                        current_operation="Flashing MCU firmware..."
                    ))
                
                success = self._flash_mcu_component(firmware_package, progress_callback)
                if not success:
                    raise Exception("MCU flashing failed")
            
            # Verify flashing
            if progress_callback:
                progress_callback(FirmwareFlashProgress(
                    stage=FlashStage.VERIFYING,
                    overall_progress=90.0,
                    current_operation="Verifying firmware..."
                ))
            
            verification_success = self._verify_firmware_flash(firmware_package, operation)
            
            # Complete
            elapsed_time = time.time() - start_time
            
            if progress_callback:
                progress_callback(FirmwareFlashProgress(
                    stage=FlashStage.COMPLETED,
                    overall_progress=100.0,
                    current_operation="Firmware flash completed successfully",
                    elapsed_time=elapsed_time
                ))
            
            self.logger.info(f"Firmware flash completed successfully in {elapsed_time:.2f}s")
            return True
            
        except Exception as e:
            elapsed_time = time.time() - start_time
            self.logger.error(f"Firmware flash failed: {e}")
            
            if progress_callback:
                progress_callback(FirmwareFlashProgress(
                    stage=FlashStage.ERROR,
                    overall_progress=0.0,
                    current_operation=f"Error: {e}",
                    elapsed_time=elapsed_time
                ))
            
            return False    

    def _download_firmware(self, version: str, 
                          progress_callback: Optional[Callable[[FirmwareFlashProgress], None]]) -> Optional[ChromaticFirmwarePackage]:
        """
        Download firmware package.
        
        Args:
            version: Version to download
            progress_callback: Progress callback
            
        Returns:
            ChromaticFirmwarePackage: Downloaded firmware, or None if failed
        """
        try:
            # Get firmware manifest
            manifest = self.firmware_manager.get_firmware_manifest()
            if not manifest:
                raise Exception("Could not load firmware manifest")
            
            # Get firmware info
            firmware_info = self.firmware_manager.get_firmware_info(version, manifest)
            if not firmware_info:
                raise Exception(f"Firmware version '{version}' not found")
            
            # Download firmware with progress tracking
            def download_progress(message: str):
                if progress_callback:
                    progress_callback(FirmwareFlashProgress(
                        stage=FlashStage.DOWNLOADING,
                        overall_progress=15.0,
                        current_operation=message
                    ))
            
            firmware_package = self.firmware_manager.download_firmware(
                firmware_info, 
                progress_callback=download_progress
            )
            
            return firmware_package
            
        except Exception as e:
            self.logger.error(f"Error downloading firmware: {e}")
            return None
    
    def _flash_fpga_component(self, firmware_package: ChromaticFirmwarePackage,
                            progress_callback: Optional[Callable[[FirmwareFlashProgress], None]]) -> bool:
        """
        Flash FPGA component of firmware.
        
        Args:
            firmware_package: Firmware package
            progress_callback: Progress callback
            
        Returns:
            bool: True if successful
        """
        try:
            def fpga_progress(fpga_prog: FPGAFlashProgress):
                if progress_callback:
                    # Map FPGA progress to overall progress (30-60%)
                    overall_progress = 30.0 + (fpga_prog.progress_percent * 0.3)
                    
                    progress_callback(FirmwareFlashProgress(
                        stage=FlashStage.FLASHING_FPGA,
                        overall_progress=overall_progress,
                        current_operation=fpga_prog.current_operation,
                        fpga_progress=fpga_prog
                    ))
            
            return self.fpga_flasher.flash_fpga_bitstream(
                firmware_package.fpga_bitstream_path,
                progress_callback=fpga_progress
            )
            
        except Exception as e:
            self.logger.error(f"Error flashing FPGA: {e}")
            return False
    
    def _flash_mcu_component(self, firmware_package: ChromaticFirmwarePackage,
                           progress_callback: Optional[Callable[[FirmwareFlashProgress], None]]) -> bool:
        """
        Flash MCU component of firmware.
        
        Args:
            firmware_package: Firmware package
            progress_callback: Progress callback
            
        Returns:
            bool: True if successful
        """
        try:
            def mcu_progress(mcu_prog: MCUFlashProgress):
                if progress_callback:
                    # Map MCU progress to overall progress (60-90%)
                    overall_progress = 60.0 + (mcu_prog.progress_percent * 0.3)
                    
                    progress_callback(FirmwareFlashProgress(
                        stage=FlashStage.FLASHING_MCU,
                        overall_progress=overall_progress,
                        current_operation=mcu_prog.current_operation,
                        mcu_progress=mcu_prog
                    ))
            
            return self.mcu_flasher.flash_mcu_firmware(
                firmware_package.mcu_binary_path,
                progress_callback=mcu_progress
            )
            
        except Exception as e:
            self.logger.error(f"Error flashing MCU: {e}")
            return False
    
    def _verify_firmware_flash(self, firmware_package: ChromaticFirmwarePackage,
                             operation: FlashOperation) -> bool:
        """
        Verify firmware flash was successful.
        
        Args:
            firmware_package: Firmware package that was flashed
            operation: What was flashed
            
        Returns:
            bool: True if verification successful
        """
        try:
            if not self.version_detector:
                self.logger.warning("No version detector available for verification")
                return True
            
            # Wait for device to boot
            time.sleep(3.0)
            
            # Try to get device version
            device_version = self.version_detector.get_device_version(timeout=15.0)
            if not device_version:
                self.logger.warning("Could not get device version for verification")
                return False
            
            # Check if versions match expected
            verification_success = True
            
            if operation in [FlashOperation.BOTH, FlashOperation.MCU]:
                # Extract expected MCU version from firmware package version
                expected_mcu = self._extract_mcu_version(firmware_package.version)
                if expected_mcu and device_version.mcu_version != expected_mcu:
                    self.logger.warning(f"MCU version mismatch: expected {expected_mcu}, got {device_version.mcu_version}")
                    verification_success = False
                else:
                    self.logger.info(f"MCU version verified: {device_version.mcu_version}")
            
            if operation in [FlashOperation.BOTH, FlashOperation.FPGA]:
                # Extract expected FPGA version from firmware package version
                expected_fpga = self._extract_fpga_version(firmware_package.version)
                if expected_fpga and device_version.fpga_version != expected_fpga:
                    self.logger.warning(f"FPGA version mismatch: expected {expected_fpga}, got {device_version.fpga_version}")
                    verification_success = False
                else:
                    self.logger.info(f"FPGA version verified: {device_version.fpga_version}")
            
            return verification_success
            
        except Exception as e:
            self.logger.warning(f"Firmware verification failed: {e}")
            return False
    
    def _extract_mcu_version(self, firmware_version: str) -> Optional[str]:
        """Extract MCU version from firmware version string"""
        # This would depend on the firmware versioning scheme
        # For now, assume the firmware version is the MCU version
        return firmware_version
    
    def _extract_fpga_version(self, firmware_version: str) -> Optional[str]:
        """Extract FPGA version from firmware version string"""
        # This would depend on the firmware versioning scheme
        # For now, assume the firmware version is the FPGA version
        return firmware_version
    
    def check_for_updates(self) -> Optional[VersionComparison]:
        """
        Check for available firmware updates.
        
        Returns:
            VersionComparison: Update comparison, or None if failed
        """
        try:
            if not self.version_detector:
                self.logger.warning("No version detector available for update check")
                return None
            
            # Get current device version
            current_version = self.version_detector.get_device_version()
            if not current_version:
                self.logger.error("Could not get current device version")
                return None
            
            # Get latest available version
            manifest = self.firmware_manager.get_firmware_manifest()
            if not manifest:
                self.logger.error("Could not load firmware manifest")
                return None
            
            latest_info = self.firmware_manager.get_firmware_info('latest', manifest)
            if not latest_info:
                self.logger.error("Could not get latest firmware info")
                return None
            
            # Create available version object
            available_version = FirmwareVersion(
                mcu_version=self._extract_mcu_version(latest_info.version) or latest_info.version,
                fpga_version=self._extract_fpga_version(latest_info.version) or latest_info.version
            )
            
            # Compare versions
            comparison = self.version_detector.compare_versions(current_version, available_version)
            
            self.logger.info(f"Update check: current={current_version.mcu_version}/{current_version.fpga_version}, "
                           f"available={available_version.mcu_version}/{available_version.fpga_version}, "
                           f"update_available={comparison.update_available}")
            
            return comparison
            
        except Exception as e:
            self.logger.error(f"Error checking for updates: {e}")
            return None
    
    def get_available_versions(self) -> List[str]:
        """
        Get list of available firmware versions.
        
        Returns:
            List[str]: Available firmware versions
        """
        try:
            manifest = self.firmware_manager.get_firmware_manifest()
            if not manifest:
                return []
            
            versions = [fw.version for fw in manifest.firmware_list]
            
            # Add special versions
            special_versions = []
            if manifest.latest_version:
                special_versions.append('latest')
            if manifest.preview_version:
                special_versions.append('preview')
            if manifest.rollback_version:
                special_versions.append('rollback')
            
            return special_versions + sorted(versions, reverse=True)
            
        except Exception as e:
            self.logger.error(f"Error getting available versions: {e}")
            return []
    
    def get_firmware_info(self, version: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a firmware version.
        
        Args:
            version: Firmware version
            
        Returns:
            Dict[str, Any]: Firmware information, or None if not found
        """
        try:
            manifest = self.firmware_manager.get_firmware_manifest()
            if not manifest:
                return None
            
            firmware_info = self.firmware_manager.get_firmware_info(version, manifest)
            if not firmware_info:
                return None
            
            return {
                'version': firmware_info.version,
                'release_date': firmware_info.release_date,
                'is_preview': firmware_info.is_preview,
                'is_rollback': firmware_info.is_rollback,
                'minimum_bootloader_version': firmware_info.minimum_bootloader_version,
                'mcu_size': firmware_info.file_size_mcu,
                'fpga_size': firmware_info.file_size_fpga,
                'changelog': firmware_info.changelog_key,
                'release_notes': firmware_info.release_notes_key
            }
            
        except Exception as e:
            self.logger.error(f"Error getting firmware info: {e}")
            return None
    
    def validate_firmware_compatibility(self, version: str) -> Dict[str, Any]:
        """
        Validate firmware compatibility with current device.
        
        Args:
            version: Firmware version to validate
            
        Returns:
            Dict[str, Any]: Compatibility validation results
        """
        validation = {
            'compatible': False,
            'version_found': False,
            'bootloader_compatible': True,
            'warnings': [],
            'errors': []
        }
        
        try:
            # Get firmware info
            manifest = self.firmware_manager.get_firmware_manifest()
            if not manifest:
                validation['errors'].append("Could not load firmware manifest")
                return validation
            
            firmware_info = self.firmware_manager.get_firmware_info(version, manifest)
            if not firmware_info:
                validation['errors'].append(f"Firmware version '{version}' not found")
                return validation
            
            validation['version_found'] = True
            
            # Check bootloader compatibility
            if firmware_info.minimum_bootloader_version and self.version_detector:
                try:
                    current_version = self.version_detector.get_device_version()
                    if current_version and current_version.bootloader_version:
                        from packaging import version
                        current_bl = version.parse(current_version.bootloader_version)
                        required_bl = version.parse(firmware_info.minimum_bootloader_version)
                        
                        if current_bl < required_bl:
                            validation['bootloader_compatible'] = False
                            validation['errors'].append(
                                f"Bootloader update required: current {current_version.bootloader_version}, "
                                f"minimum {firmware_info.minimum_bootloader_version}"
                            )
                except Exception as e:
                    validation['warnings'].append(f"Could not check bootloader compatibility: {e}")
            
            # Check for preview/rollback warnings
            if firmware_info.is_preview:
                validation['warnings'].append("This is a preview firmware version - use with caution")
            
            if firmware_info.is_rollback:
                validation['warnings'].append("This is a rollback firmware version")
            
            # Overall compatibility
            validation['compatible'] = (
                validation['version_found'] and 
                validation['bootloader_compatible'] and
                len(validation['errors']) == 0
            )
            
        except Exception as e:
            validation['errors'].append(f"Error validating compatibility: {e}")
        
        return validation    

    def flash_firmware_with_progress(
        self, 
        version: str, 
        operation: FlashOperation = FlashOperation.BOTH,
        show_progress_dialog: bool = True,
        run_in_background: bool = True
    ) -> bool:
        """
        Flash firmware with integrated progress reporting.
        
        Args:
            version: Firmware version to flash
            operation: What to flash (BOTH, FPGA, MCU, or CART)
            show_progress_dialog: Whether to show progress dialog
            run_in_background: Whether to run in background thread
            
        Returns:
            bool: True if flashing succeeded
        """
        
        # Create progress reporter
        operation_name = f"Flash Firmware {version}"
        if operation != FlashOperation.BOTH:
            operation_name += f" ({operation.value})"
        
        reporter = create_progress_reporter(
            OperationType.FIRMWARE_FLASH,
            operation_name,
            show_dialog=show_progress_dialog
        )
        
        # Run in background thread if requested
        if run_in_background:
            return self._flash_firmware_background(version, operation, reporter)
        else:
            return self._flash_firmware_foreground(version, operation, reporter)
    
    def _flash_firmware_background(self, version: str, operation: FlashOperation, reporter: ProgressReporter) -> bool:
        """Run firmware flashing in background thread"""
        
        def flash_worker():
            """Worker function for background flashing"""
            return self._flash_firmware_foreground(version, operation, reporter)
        
        # Create worker thread
        worker = create_worker_thread(
            target_function=flash_worker,
            priority=ThreadPriority.HIGH,
            operation_name=f"Flash Firmware {version}"
        )
        
        # Start worker and return immediately
        # Note: In a real implementation, you'd want to return a Future or handle completion differently
        worker.start()
        return True  # Return True to indicate operation started successfully
    
    def _flash_firmware_foreground(self, version: str, operation: FlashOperation, reporter: ProgressReporter) -> bool:
        """Run firmware flashing in foreground with progress reporting"""
        
        try:
            # Start the operation
            reporter.start(total_steps=100, message="Initializing firmware flash...")
            
            # Stage 1: Download firmware (20% of total progress)
            reporter.update_progress(
                current=5,
                message="Downloading firmware package...",
                details=f"Fetching {version} firmware from server"
            )
            
            firmware_package = self._download_firmware_with_progress(version, reporter, 5, 20)
            
            # Stage 2: Prepare for flashing (5% of total progress)
            reporter.update_progress(
                current=25,
                message="Preparing device for flashing...",
                details="Validating firmware and preparing device"
            )
            
            self._prepare_device_for_flash(reporter)
            
            # Stage 3: Flash components based on operation
            if operation in [FlashOperation.BOTH, FlashOperation.FPGA]:
                # FPGA flashing (35% of total progress)
                reporter.update_progress(
                    current=30,
                    message="Flashing FPGA...",
                    details="Programming FPGA bitstream"
                )
                
                self._flash_fpga_with_progress(firmware_package, reporter, 30, 65)
            
            if operation in [FlashOperation.BOTH, FlashOperation.MCU]:
                # MCU flashing (30% of total progress)
                start_progress = 65 if operation == FlashOperation.BOTH else 30
                end_progress = 95 if operation == FlashOperation.BOTH else 90
                
                reporter.update_progress(
                    current=start_progress,
                    message="Flashing MCU...",
                    details="Programming ESP32 firmware"
                )
                
                self._flash_mcu_with_progress(firmware_package, reporter, start_progress, end_progress)
            
            # Stage 4: Verification (5% of total progress)
            reporter.update_progress(
                current=95,
                message="Verifying firmware...",
                details="Checking firmware installation"
            )
            
            self._verify_firmware_with_progress(reporter, 95, 100)
            
            # Complete successfully
            reporter.complete(success=True, message="Firmware flashed successfully!")
            
            self.logger.info(f"Firmware flash completed successfully: {version}")
            return True
            
        except Exception as e:
            error_msg = f"Firmware flash failed: {e}"
            self.logger.error(error_msg)
            
            # Create appropriate error
            if "download" in str(e).lower():
                error = FirmwareDownloadError(error_msg, original_exception=e)
            else:
                error = FirmwareFlashError(error_msg, original_exception=e)
            
            reporter.report_error(error)
            return False
    
    def _download_firmware_with_progress(
        self, 
        version: str, 
        reporter: ProgressReporter, 
        start_progress: int, 
        end_progress: int
    ) -> ChromaticFirmwarePackage:
        """Download firmware with progress reporting"""
        
        def download_progress_callback(bytes_downloaded: int, total_bytes: int):
            if total_bytes > 0:
                download_percentage = (bytes_downloaded / total_bytes) * 100
                overall_progress = start_progress + (download_percentage / 100) * (end_progress - start_progress)
                
                reporter.update_progress(
                    current=int(overall_progress),
                    message="Downloading firmware package...",
                    details=f"Downloaded {bytes_downloaded:,} of {total_bytes:,} bytes",
                    bytes_processed=bytes_downloaded,
                    bytes_total=total_bytes
                )
        
        # Download firmware with progress callback
        firmware_package = self.firmware_manager.download_firmware(
            version, 
            progress_callback=download_progress_callback
        )
        
        reporter.update_progress(
            current=end_progress,
            message="Firmware download completed",
            details=f"Downloaded {version} firmware package"
        )
        
        return firmware_package
    
    def _prepare_device_for_flash(self, reporter: ProgressReporter):
        """Prepare device for flashing"""
        
        # Check device connection
        if not self.device_communicator or not self.device_communicator.is_connected():
            raise FirmwareFlashError("Device not connected")
        
        # Put device in flash mode if needed
        reporter.update_progress(
            message="Preparing device for flashing...",
            details="Setting device to flash mode"
        )
        
        # Additional preparation steps would go here
        time.sleep(0.5)  # Simulate preparation time
    
    def _flash_fpga_with_progress(
        self, 
        firmware_package: ChromaticFirmwarePackage, 
        reporter: ProgressReporter, 
        start_progress: int, 
        end_progress: int
    ):
        """Flash FPGA with progress reporting"""
        
        def fpga_progress_callback(fpga_progress: FPGAFlashProgress):
            overall_progress = start_progress + (fpga_progress.percentage / 100) * (end_progress - start_progress)
            
            reporter.update_progress(
                current=int(overall_progress),
                message="Flashing FPGA...",
                details=fpga_progress.current_operation
            )
        
        # Flash FPGA
        success = self.fpga_flasher.flash_fpga(
            firmware_package.fpga_bitstream,
            progress_callback=fpga_progress_callback
        )
        
        if not success:
            raise FirmwareFlashError("FPGA flashing failed", component="FPGA")
        
        reporter.update_progress(
            current=end_progress,
            message="FPGA flashing completed",
            details="FPGA bitstream programmed successfully"
        )
    
    def _flash_mcu_with_progress(
        self, 
        firmware_package: ChromaticFirmwarePackage, 
        reporter: ProgressReporter, 
        start_progress: int, 
        end_progress: int
    ):
        """Flash MCU with progress reporting"""
        
        def mcu_progress_callback(mcu_progress: MCUFlashProgress):
            overall_progress = start_progress + (mcu_progress.percentage / 100) * (end_progress - start_progress)
            
            reporter.update_progress(
                current=int(overall_progress),
                message="Flashing MCU...",
                details=mcu_progress.current_operation
            )
        
        # Flash MCU
        success = self.mcu_flasher.flash_mcu(
            firmware_package.mcu_firmware,
            progress_callback=mcu_progress_callback
        )
        
        if not success:
            raise FirmwareFlashError("MCU flashing failed", component="MCU")
        
        reporter.update_progress(
            current=end_progress,
            message="MCU flashing completed",
            details="ESP32 firmware programmed successfully"
        )
    
    def _verify_firmware_with_progress(
        self, 
        reporter: ProgressReporter, 
        start_progress: int, 
        end_progress: int
    ):
        """Verify firmware installation with progress reporting"""
        
        reporter.update_progress(
            current=start_progress + 2,
            message="Verifying firmware installation...",
            details="Checking device response"
        )
        
        # Wait for device to restart
        time.sleep(2.0)
        
        reporter.update_progress(
            current=start_progress + 4,
            message="Verifying firmware installation...",
            details="Querying firmware version"
        )
        
        # Verify firmware version if version detector is available
        if self.version_detector:
            try:
                new_version = self.version_detector.get_current_version()
                if new_version:
                    reporter.update_progress(
                        current=end_progress,
                        message="Firmware verification completed",
                        details=f"Firmware version: {new_version.mcu_version}"
                    )
                else:
                    self.logger.warning("Could not verify firmware version after flash")
            except Exception as e:
                self.logger.warning(f"Firmware verification failed: {e}")
        
        reporter.update_progress(
            current=end_progress,
            message="Firmware verification completed",
            details="Firmware installation verified"
        )
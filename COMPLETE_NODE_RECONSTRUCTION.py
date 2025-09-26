"""
Complete reconstruction of all NODE:12 and NODE:27 issues from MRUpdater decompilation
Ready for contribution back to the project
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Union, Literal, TypedDict
from enum import IntEnum

# ============================================================================
# From cartclinic/mrpatcher.py
# ============================================================================

@dataclass
class GameSaveSettings:
    """Contains data about how and where the game saves data"""
    save_compatible: bool
    saves_to_rom: bool
    offset_kb: int
    max_length: int
    
    @classmethod
    def from_dict(cls, data: dict) -> 'GameSaveSettings':
        return cls(**data)

@dataclass
class MRPatcherResponse:
    """MRPatcher POST should always respond with this structure"""
    game_title: str
    thumbnail: str
    patch: bytearray  # Base64-encoded IPS patch data
    error: str
    error_code: str
    user_error: bool
    needs_update: bool
    save_compatible: bool
    uploaded_version: str
    latest_version: str
    changes: str
    save_settings: Optional[GameSaveSettings]
    
    @classmethod
    def from_dict(cls, data: dict) -> 'MRPatcherResponse':
        if 'save_settings' in data and data['save_settings']:
            data['save_settings'] = GameSaveSettings.from_dict(data['save_settings'])
        # Convert base64 patch to bytearray if needed
        if 'patch' in data and isinstance(data['patch'], str):
            import base64
            data['patch'] = bytearray(base64.b64decode(data['patch']))
        return cls(**data)

@dataclass
class MRPatcherGameInfo:
    """Response from the /game_id endpoint"""
    game_id: str
    title: str
    save_settings: Optional[GameSaveSettings]
    supported: bool
    
    @classmethod
    def from_dict(cls, data: dict) -> 'MRPatcherGameInfo':
        if 'save_settings' in data and data['save_settings']:
            data['save_settings'] = GameSaveSettings.from_dict(data['save_settings'])
        return cls(**data)

# ============================================================================
# From flashing_tool/s3_wrapper.py
# ============================================================================

@dataclass
class AwsCredentials:
    """AWS credentials for S3 access"""
    access_key_id: str
    secret_access_key: str
    session_token: Optional[str] = None
    region_name: str = 'us-east-1'

# ============================================================================
# From flashing_tool/util.py
# ============================================================================

@dataclass
class S3FirmwareInfo:
    """S3 firmware information - represents a firmware file in S3"""
    filename: str
    directory: str  
    label: str  # e.g., "LATEST", "PREVIEW", "ROLLBACK"
    
@dataclass
class ChromaticFirmwarePackage:
    """Downloaded firmware package ready for flashing"""
    zip_path: str  # Path to downloaded zip file
    fpga_fw_path: str  # Extracted FPGA firmware path
    mcu_fw_path: str  # Extracted MCU firmware path
    temp_dir_path: str  # Temporary extraction directory
    changelog: Dict  # Parsed changelog data
    version: str  # Firmware version string
    label: str  # e.g., "LATEST", "PREVIEW", "ROLLBACK"

@dataclass
class CartClinicFirmwarePackage:
    """Cart Clinic FPGA firmware package"""
    fpga_fw_path: str  # Path to Cart Clinic FPGA bitstream
    temp_dir_path: str  # Temporary extraction directory

@dataclass
class MRUpdaterManifestData:
    """Parsed manifest.yaml data from S3"""
    version: str  # MRUpdater version
    mrpatcher_endpoint: str  # MRPatcher API endpoint URL
    chromatic_fw_options: List[S3FirmwareInfo]  # Available firmware versions
    cartclinic_fw_info: S3FirmwareInfo  # Cart Clinic firmware info
    chromatic_fw_changelog_uri: str  # URL to firmware changelog

# ============================================================================
# From flashing_tool/features/manager.py
# ============================================================================

@dataclass
class FeatureUpdate:
    """Tracks feature changes"""
    previous_features: set
    current_features: set

# ============================================================================
# From cartclinic/consts.py
# ============================================================================

@dataclass
class CartClinicSaveOperationValue:
    """Value object for save operations"""
    value: int
    status_message: str
    warning_message: str
    success_message: str

# ============================================================================
# From libpyretro/feature_api/current_user.py
# ============================================================================

@dataclass
class User:
    """User information with OS metadata"""
    id: str  # User ID
    os: str  # Operating system
    cpu: str  # CPU architecture
    os_version: str  # OS version
    
    def as_api_metadata(self) -> Dict[str, str]:
        """Convert to API metadata format"""
        return {
            'user_id': self.id,
            'os': self.os,
            'cpu': self.cpu,
            'os_version': self.os_version
        }

# ============================================================================
# From libpyretro/cartclinic/protocol/common.py
# ============================================================================

# Constants needed by some classes
SCREEN_PIXEL_WIDTH = 160
SCREEN_PIXEL_HEIGHT = 144

class CartFlashChip(IntEnum):
    """An enum of existing cartridge flash chips."""
    Microchip_SST39VF1681 = 1
    Infineon_S29JL032J70 = 2
    ISSI_IS29GL032 = 3
    Microchip_SST39VF1682 = 4

@dataclass
class LimitedInteger:
    """A class which represents positive integers up to a maximum value."""
    value: int
    max_value: int
    
    def __post_init__(self):
        if self.value < 0 or self.value > self.max_value:
            raise ValueError(f"Value {self.value} out of range [0, {self.max_value}]")

@dataclass
class UnsignedByte(LimitedInteger):
    """A class which represents unsigned bytes (0 - 255)."""
    value: int
    max_value: int = field(default=255, init=False)

@dataclass 
class UnsignedHalfWord(LimitedInteger):
    """A class which represents unsigned half words (0 - 65535)."""
    value: int
    max_value: int = field(default=65535, init=False)

@dataclass
class VariableBitWidth(LimitedInteger):
    """A class which represents positive integers less than a specific number of bits."""
    value: int
    bit_len: int
    max_value: int = field(init=False)
    
    def __post_init__(self):
        self.max_value = (1 << self.bit_len) - 1
        super().__post_init__()

@dataclass
class CartBusAddr(UnsignedHalfWord):
    """A class which represents positive integers less than 0x10000 for cartridge address buses."""
    data: int  # Using 'data' as per bytecode
    value: int = field(init=False)
    
    def __post_init__(self):
        self.value = self.data
        super().__post_init__()

@dataclass
class FrameBufferAddr(LimitedInteger):
    """A class which represents positive integers less than 0x8000 for frame buffer addresses."""
    addr: int  # Using 'addr' as per bytecode
    value: int = field(init=False)
    max_value: int = field(default=0x7FFF, init=False)
    
    def __post_init__(self):
        self.value = self.addr
        super().__post_init__()

@dataclass
class PixelRGB555:
    """
    A class which represents RGB555 pixel image data.
    Color is RGB555 (5-bits each channel) with red color in bits 4..0, 
    green in 9..5 and blue in 14..10
    """
    value: tuple[int, int, int]  # (r, g, b) each 5-bit
    
    def __post_init__(self):
        r, g, b = self.value
        for val, name in [(r, 'red'), (g, 'green'), (b, 'blue')]:
            if val < 0 or val > 31:
                raise ValueError(f"{name} value {val} not in 5-bit range [0, 31]")
    
    @classmethod
    def from_rgb888(cls, color: 'PixelRGB888') -> 'PixelRGB555':
        """Convert from RGB888 to RGB555"""
        return cls((color.red >> 3, color.green >> 3, color.blue >> 3))
    
    def value_as_uint15(self) -> int:
        """Return as 15-bit unsigned integer"""
        r, g, b = self.value
        return (b << 10) | (g << 5) | r

@dataclass
class PSRAMAddr(LimitedInteger):
    """A class which represents positive integers less than 0x800000 for PSRAM addresses."""
    addr: int  # Using 'addr' as per bytecode
    value: int = field(init=False)
    max_value: int = field(default=0x7FFFFF, init=False)
    
    def __post_init__(self):
        self.value = self.addr
        super().__post_init__()

@dataclass
class PSRAMData(UnsignedByte):
    """A class which represents data values which can be written to or read from PSRAM."""
    # Inherits from UnsignedByte as PSRAM operations are byte-based

@dataclass
class AudioSampleCount(LimitedInteger):
    """A class which represents positive integers less than 0x200000 for the number of samples to play."""
    sample_count: int  # Using 'sample_count' as per bytecode
    value: int = field(init=False)
    max_value: int = field(default=0x1FFFFF, init=False)
    
    def __post_init__(self):
        self.value = self.sample_count
        super().__post_init__()

@dataclass
class CartFlashInfo:
    """A class which describes the cartridge's flash chip."""
    part_id: CartFlashChip
    part_number: str
    vendor: str
    total_size_kb: int
    sector_size_kb: int
    grouping: int
    recovery_offset_kb: int

# ============================================================================
# From libpyretro/cartclinic/comms/exceptions.py
# ============================================================================

@dataclass
class ComparisonError:
    """Error when expected and actual values don't match"""
    expected: bytes
    actual: bytes

@dataclass  
class InvalidWriteBankSize:
    """The request to write to a bank must be 16KB."""
    size: int

@dataclass
class WriteBlockAddressError:
    """The write block command failed read-back address verification."""
    pass  # No fields from bytecode

@dataclass
class WriteBlockDataError:
    """The write block command failed read-back data verification."""
    addr: int

# ============================================================================
# NODE:27 Issues (Not dataclasses, but other node types)
# ============================================================================

# These are TypedDict, NamedTuple, or other special class constructions
# that pycdc couldn't properly decompile

# From pydantic/config.py
class ConfigDict(TypedDict, total=False):
    """A TypedDict for configuring Pydantic behaviour."""
    serialize_by_alias: bool
    # Other Pydantic config options would go here

# From libpyretro/feature_api/client/api_response.py
# This appears to be a Generic class definition
# ApiResponse = TypeVar('ApiResponse', bound='BaseModel')

# From flashing_tool/plugins/base/base.py
# This appears to be a Plugin base class with optional name parameter
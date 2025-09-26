# MRUpdater Reassembled Code Summary

## Overview
Successfully decompiled the MRUpdater.exe Python application using a patched version of pycdc to handle Python 3.10 opcodes. The application is a Qt-based firmware updater and cartridge management tool for the ModRetro Chromatic gaming device.

## Key Components

### 1. Main Application (main.py)
- **GUI Framework**: PySide6 (Qt for Python)
- **Feature API URLs**:
  - Development: `https://8xlzcdo2o6.execute-api.us-east-1.amazonaws.com`
  - Production: `https://7hcmw5socl.execute-api.us-east-1.amazonaws.com`
- **Main Features**:
  - Firmware updates from S3 bucket
  - Cart Clinic for ROM patching
  - Feature management with activation codes

### 2. MRPatcher API (cartclinic/mrpatcher.py)
```python
class MRPatcherAPI:
    def __init__(self, endpoint):
        self.endpoint = endpoint
        self._headers = {
            'Content-Type': 'application/octet-stream',
            'X-MR-Client-Version': __version_sha__,
            'X-MR-Client-MAC': get_device_id(),  # SHA256 of MAC address
            'X-MR-Client-Platform-System': platform.system(),
            'X-MR-Client-Platform-Architecture': platform.machine(),
            'X-MR-Client-Platform-Version': platform.version(),
            'X-MR-Client-Expected-Response-Version': '2.0'
        }
    
    def request_patch(self, game_binary):
        # POST full ROM to endpoint
        res = requests.post(self.endpoint, headers=self._headers, 
                          data=game_binary, timeout=MRPATCHER_TIMEOUT_S)
        return MRPatcherResponse.from_dict(res.json())
    
    def get_game_id(self, game_binary):
        # POST first 512 bytes to /game_id endpoint
        game_id_block = game_binary[:512]
        res = requests.post(f"{self.endpoint}/game_id", headers=self._headers,
                          data=game_id_block, timeout=MRPATCHER_TIMEOUT_S)
        return MRPatcherGameInfo.from_dict(res.json())
```

### 3. S3 Configuration (flashing_tool/s3_wrapper.py)
```python
REGION_NAME = 'us-east-1'
BUCKET_NAME = 'updates.modretro.com'
MANIFEST_KEY = 'apps/manifest.yaml'
DEFAULT_AUTHENTICATION = {
    'config': boto3.session.Config(signature_version=UNSIGNED)
}
```

### 4. Cart Clinic Workflow (cartclinic/cc_subprocess.py)
1. **CartClinicCheckSubprocess**: 
   - Reads cartridge data
   - Requests patch from MRPatcher API
   - Receives IPS patch as base64

2. **CartClinicUpdateSubprocess**:
   - Applies IPS patch to ROM
   - Writes patched ROM back to cartridge
   - Manages save data

### 5. Communication Protocol (libpyretro/cartclinic/comms/session.py)
- USB/Serial communication with Chromatic device
- Bank switching for cartridge access (16KB banks)
- FRAM support for save data
- Command IDs for various operations

### 6. Feature Management (flashing_tool/features/manager.py)
- Activation code system
- Feature flags:
  - `mrupdater.system:preview-firmware`
  - `mrupdater.system:rollback-firmware`
- Remote feature checking via API

## API Endpoints Discovered

1. **Feature API** (for activation codes and features):
   - Dev: `https://8xlzcdo2o6.execute-api.us-east-1.amazonaws.com`
   - Prod: `https://7hcmw5socl.execute-api.us-east-1.amazonaws.com`

2. **MRPatcher API** (for ROM patching):
   - Base: `https://cbzr2zpag5.execute-api.us-east-1.amazonaws.com/default/MRPatcher`
   - Game ID: `{base}/game_id`

3. **S3 Bucket**:
   - `https://s3.us-east-1.amazonaws.com/updates.modretro.com/`
   - Contains firmware files, manifest, and updater

## Patching Process
1. User inserts cartridge
2. MRUpdater reads ROM data via USB
3. Sends ROM to MRPatcher API
4. Receives IPS patch if game is supported
5. Applies patch locally
6. Writes patched ROM back to cartridge

## Security Features
- Device ID is SHA256 hash of MAC address
- Unsigned S3 access (public bucket)
- Platform tracking in API requests
- Version checking via manifest

## Limitations in Decompilation
- Some dataclass definitions show as `<NODE:12>`
- Exception handling blocks are partially incomplete
- Some lambda expressions are mangled
- But core logic and API interactions are fully readable
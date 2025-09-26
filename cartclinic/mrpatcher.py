# Source Generated with Decompyle++
# File: mrpatcher.pyc (Python 3.10)

import logging
import requests
import platform
import hashlib
import uuid
from dataclasses import dataclass, fields
from cartclinic.consts import MRPATCHER_TIMEOUT_S
from config import __version_sha__
flashing_tool_logger = logging.getLogger('mrupdater')
MRPATCHER_RESPONSE_VERSION = '2.0'
GAME_ID_SIZE = 512
GameSaveSettings = dataclass(<NODE:12>)
MRPatcherResponse = dataclass(<NODE:12>)
MRPatcherGameInfo = dataclass(<NODE:12>)

def get_device_id():
    '''Returns a hashed unique device ID based on the MAC address'''
    mac = hex(uuid.getnode())[2:].zfill(12)
    return hashlib.sha256(mac.encode()).hexdigest()


class MRPatcherAPI:
    
    def __init__(self, endpoint):
        self.endpoint = endpoint
        self._headers = {
            'Content-Type': 'application/octet-stream',
            'X-MR-Client-Version': __version_sha__,
            'X-MR-Client-MAC': get_device_id(),
            'X-MR-Client-Platform-System': platform.system(),
            'X-MR-Client-Platform-Architecture': platform.machine(),
            'X-MR-Client-Platform-Version': platform.version(),
            'X-MR-Client-Expected-Response-Version': MRPATCHER_RESPONSE_VERSION }

    
    def test_connection(self = None):
        '''Check connection to patching service with a GET request'''
        pass
        # TODO: Implementation needed
        raise NotImplementedError("Method not implemented")
    def request_patch(self = None, game_binary = None):
        '''Requests a game patch from the service on the given ROM.'''
        res = requests.post(self.endpoint, self._headers, game_binary, MRPATCHER_TIMEOUT_S, **('headers', 'data', 'timeout'))
        return MRPatcherResponse.from_dict(res.json())

    
    def get_game_id(self = None, game_binary = None):
        '''Requests game id and save settings using just the ID portion of a given ROM.'''
        game_id_block = game_binary[:GAME_ID_SIZE]
        res = requests.post(f'''{self.endpoint}/game_id''', self._headers, game_id_block, MRPATCHER_TIMEOUT_S, **('headers', 'data', 'timeout'))
        return MRPatcherGameInfo.from_dict(res.json())



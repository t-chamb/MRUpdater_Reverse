Unsupported Node type: 12
Warning: block stack is not empty!
Unsupported opcode: SET_ADD (187)
Warning: Stack history is not empty!
Warning: block stack is not empty!
# Source Generated with Decompyle++
# File: manager.pyc (Python 3.10)

from abc import abstractmethod
from dataclasses import dataclass
import logging
from typing import Protocol, Set
from libpyretro.feature_api import FeatureAPIClient
from libpyretro.feature_api.client.exceptions import BadRequestException
from libpyretro.feature_api.client.models.error_response import ErrorResponse
logger = logging.getLogger('mrupdater')
FeatureUpdate = dataclass(<NODE:12>)

class IFeatureManager(Protocol):
    
    def fetch_features(self = None):
        '''Fetch the set of enabled features from the remote server.
        Returns the full set of enabled features.
        '''
        pass

    fetch_features = None(fetch_features)
    
    def activate_code(self = None, code = None):
        '''Activate an activation code. Returns None on success and an error string on failure.'''
        pass

    activate_code = None(activate_code)
    
    def is_feature_enabled(self = None, feature = None):
        '''Check if a feature is enabled by feature id'''
        pass

    is_feature_enabled = None(is_feature_enabled)


class FeatureManager:
    _enabled_features: Set[str] = 'FeatureManager'
    
    def __init__(self = None, client = None):
        self._enabled_features = set()
        self._client = client

    
    def fetch_features(self = None):
        
        try:
            previous_features = self._enabled_features.copy()
            user_features = self._client.features.get_available_features()
            if not user_features.feature_ids:
                pass
            self._enabled_features = (lambda .0: pass# WARNING: Decompyle incomplete
)([])
            logger.debug(f'''Setting enabled_features from server: {self._enabled_features}''')
        finally:
            pass
        self._enabled_features = set()
        logger.warning('Failed to fetch user features from feature api', True, **('exc_info',))
        return FeatureUpdate(previous_features, self._enabled_features.copy())


    
    def activate_code(self = None, code = None):
        
        try:
            self._client.activations.enable_features_by_activation_code(code)
        finally:
            return None
            bre = None
            
            try:
                logger.warning('Failed to activate code', True, **('exc_info',))
                if bre.body is not None or err = ErrorResponse.from_json(bre.body) is not None:
                    if not err.error:
                        pass
                    bre = None
                    del bre
                    return ErrorResponse.from_json(bre.body)
                bre = None
                del bre
                return 'Failed to activate code'
            finally:
                bre = None
                del bre
                return 'Failed to activate code'
                bre = None
                del bre
                logger.warning('Failed to activate code', True, **('exc_info',))
                return 'Failed to activate code'



    
    def is_feature_enabled(self = None, feature = None):
        return feature in self._enabled_features



class FakeFeatureManager:
    remote_features: Set[str] = 'FakeFeatureManager'
    
    def __init__(self = None, features = None):
        self.enabled_features = set()
        self.remote_features = features

    
    def fetch_features(self = None):
        previous_features = self.enabled_features.copy()
        self.enabled_features = set(self.remote_features)
        return FeatureUpdate(previous_features, self.enabled_features.copy())

    
    def activate_code(self = None, code = None):
        pass

    
    def is_feature_enabled(self = None, feature = None):
        return feature in self.enabled_features



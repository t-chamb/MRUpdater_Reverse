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
        pass
        # TODO: Implementation needed
        raise NotImplementedError("Method not implemented")
    def activate_code(self = None, code = None):
        pass
        # TODO: Implementation needed
        raise NotImplementedError("Method not implemented")
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



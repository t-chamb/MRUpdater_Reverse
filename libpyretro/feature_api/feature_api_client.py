# Source Generated with Decompyle++
# File: feature_api_client.pyc (Python 3.10)

from typing import Optional
import certifi
from libpyretro.feature_api.client import ActivationsApi, ApiClient, Configuration, FeaturesApi
from libpyretro.feature_api.current_user import get_current_user

class UserNotFoundError(Exception):
    '''Raised when the current user could not be found.'''
    pass


class FeatureAPIClient:
    
    def __init__(self = None, host = None, api_key = None):
        configuration = Configuration(host, api_key, certifi.where(), **('host', 'api_key', 'ssl_ca_cert'))
        self._api_client = ApiClient(configuration, **('configuration',))
        current_user = get_current_user()
        if current_user is None:
            raise UserNotFoundError('The current user could not be found.')
        self._api_client.default_headers.update(current_user.as_api_metadata())
        self.features = FeaturesApi(self._api_client, **('api_client',))
        self.activations = ActivationsApi(self._api_client, **('api_client',))



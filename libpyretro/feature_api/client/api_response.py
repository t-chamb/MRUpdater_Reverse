# Source Generated with Decompyle++
# File: api_response.pyc (Python 3.10)

'''API response object.'''
from __future__ import annotations
from typing import Optional, Generic, Mapping, TypeVar
from pydantic import Field, StrictInt, StrictBytes, BaseModel
T = TypeVar('T')

def ApiResponse():
    '''ApiResponse'''
    __doc__ = '\n    API response object\n    '
    status_code: 'StrictInt' = Field('HTTP status code', **('description',))
    headers: 'Optional[Mapping[str, str]]' = Field(None, 'HTTP headers', **('description',))
    data: 'T' = Field('Deserialized data given the data type', **('description',))
    raw_data: 'StrictBytes' = Field('Raw data (HTTP response body)', **('description',))
    model_config = {
        'arbitrary_types_allowed': True }

ApiResponse = <NODE:27>(ApiResponse, 'ApiResponse', BaseModel, Generic[T])

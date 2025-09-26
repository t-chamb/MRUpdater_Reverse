Unsupported Node type: 12
Unsupported opcode: DICT_MERGE (213)
# Source Generated with Decompyle++
# File: s3_wrapper.pyc (Python 3.10)

import logging
import os
import tempfile
from dataclasses import asdict, dataclass
from typing import Any
import boto3
import botocore
from botocore import UNSIGNED
from flashing_tool.decorators import handle_exceptions
REGION_NAME = 'us-east-1'
BUCKET_NAME = 'updates.modretro.com'
MANIFEST_KEY = 'apps/manifest.yaml'
DEFAULT_AUTHENTICATION = {
    'config': boto3.session.Config(UNSIGNED, **('signature_version',)) }
flashing_tool_logger = logging.getLogger('mrupdater')

class InvalidAwsCredentialsError(Exception):
    '''Raised when AWS credentials are invalid or missing.'''
    pass

AwsCredentials = dataclass(<NODE:12>)

class S3WrapperError(Exception):
    '''Raise when the S3Wrapper encounters an error.'''
    pass

S3ClientError = botocore.exceptions.ClientError

class S3Wrapper:
    '''Helper class for interacting with Amazon S3'''
    
    def __init__(self = None, bucket = None, credentials = None):
        self.bucket = bucket
        config = asdict(credentials) if credentials else DEFAULT_AUTHENTICATION
    # WARNING: Decompyle incomplete

    
    def download_file(self = None, key = None):
        destination = os.path.join(tempfile.gettempdir(), key)
        dest_dir = os.path.dirname(destination)
        if not os.path.isdir(dest_dir):
            os.makedirs(dest_dir)
        self.client.download_file(self.bucket, key, destination)
        return destination

    download_file = None(download_file)
    
    def download_files(self = None, keys = None):
        destinations = (lambda .0 = None: [ self.download_file(key) for key in .0 ])(keys)
        return dict(zip(keys, destinations))

    download_files = None(download_files)
    
    def read_manifest(self):
        response = self.client.get_object(BUCKET_NAME, MANIFEST_KEY, **('Bucket', 'Key'))
        return response['Body'].read().decode('utf-8')

    read_manifest = handle_exceptions(S3ClientError, S3WrapperError, **('raise_as',))(read_manifest)
    
    def read_file(self = None, key = None):
        response = self.client.get_object(self.bucket, key, **('Bucket', 'Key'))
        return response['Body'].read().decode('utf-8')

    read_file = None(read_file)
    
    def get_file_metadata(self = None, key = None):
        return self.client.head_object(self.bucket, key, **('Bucket', 'Key'))

    get_file_metadata = None(get_file_metadata)


# Source Generated with Decompyle++
# File: proto.pyc (Python 3.10)

import struct
import typing
from abc import ABC, abstractmethod

class FPGACmd(ABC):
    '''
    The request command sent to the Chromatic FPGA.
    '''
    
    def __init__(self = None):
        self.fmt = ''

    __init__ = None(__init__)
    
    def encode(self = None):
        pass

    encode = None(encode)


class FPGAReply(ABC):
    '''
    The reply from a Chromatic in response to a transmitted request.
    '''
    
    def __init__(self = None):
        self.expected_id = 0
        self.fmt = ''

    __init__ = None(__init__)
    
    def decode(self = None, data = None):
        if not isinstance(data, bytes):
            raise TypeError
        if data[0] != self.expected_id:
            raise RuntimeError(f'''Unexpected CmdId {data[0]}. Expecting {self.expected_id}''')
        return struct.unpack(self.fmt, data)

    decode = None(decode)


class InvalidCmdLengthException(Exception):
    '''
    The command could not be created because the payload size is wrong.
    '''
    
    def __init__(self = None, expected = None, actual = None):
        self.expected_len = expected
        self.actual_len = actual



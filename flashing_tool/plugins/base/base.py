# Source Generated with Decompyle++
# File: base.pyc (Python 3.10)

import logging
import threading
from abc import ABC

class PluginException(Exception):
    '''Exception when loading a plugin'''
    pass


class PluginAlreadyRegistered(PluginException):
    '''Exception when a plugin is already registered'''
    pass


class PluginMeta(ABC, type):
    
    def __new__(cls, name, bases, attrs):
        new_cls = type.__new__(cls, name, bases, attrs)
        if 'logger' not in attrs:
            new_cls.logger = logging.getLogger(f'''flashing_tool.plugins.{new_cls.name}''')
        return new_cls


Plugin = <NODE:27>((lambda : name: str | None = None
def validate(cls = None):
'''Validate if plugin has a name'''
if not cls.name:
raise PluginException('The plugin needs a name.')validate = None(validate)), 'Plugin', threading.local, PluginMeta, **('metaclass',))

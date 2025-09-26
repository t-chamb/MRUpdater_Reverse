# Source Generated with Decompyle++
# File: tab.pyc (Python 3.10)

from abc import abstractmethod
from typing import Any
from PySide6.QtWidgets import QWidget, QMainWindow
from flashing_tool.plugins.base import Plugin

class TabComponentPlugin(Plugin):
    '''Base class for plugins that add a new tab to the update tool.'''
    
    def __init__(self = None):
        super().__init__()
        self.tab_ui = None
        self.main_window = None
        self.tab_container = QWidget()

    
    def render(self = None, main_window = None):
        self.main_window = main_window
        self._setup_tab_ui()
        self._register_event_handlers()
        self._post_render()

    
    def _setup_tab_ui(self = None):
        """Renders the tab's UI on the main application window."""
        raise NotImplementedError()

    _setup_tab_ui = None(_setup_tab_ui)
    
    def _register_event_handlers(self = None):
        pass

    _register_event_handlers = None(_register_event_handlers)
    
    def quit(self = None):
        pass

    quit = None(quit)
    
    def tab_ui_class(self = None):
        '''The Ui_* class for the compiled .ui file for the tab'''
        raise NotImplementedError()

    tab_ui_class = None(None(tab_ui_class))
    
    def _post_render(self = None):
        '''Actions to be performed after rendering the UI.

        For example, the plugin may want to toggle the display of certain
        components in the application.
        '''
        pass

    _post_render = None(_post_render)
    __classcell__ = None


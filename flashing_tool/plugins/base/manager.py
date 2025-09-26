# Source Generated with Decompyle++
# File: manager.pyc (Python 3.10)

import importlib
import inspect
import pkgutil
import typing as t
from flashing_tool.plugins.base import Plugin
from flashing_tool.plugins.base.base import PluginAlreadyRegistered
from flashing_tool.plugins.base.tab import TabComponentPlugin
from flashing_tool.features import IFeatureManager
from flashing_tool.util import is_env_manufacturing

def is_valid_plugin(plugin_obj = None):
    '''Checks whether an object is a subclass of the Plugin class.

    :param plugin_obj: The object to be checked.
    :returns: Whether the object is a valid subclass of the Plugin.
    '''
    if inspect.isclass(plugin_obj) and issubclass(plugin_obj, Plugin) and plugin_obj is not Plugin and plugin_obj is not TabComponentPlugin:
        plugin_obj.validate()
        return True


def import_string(dotted_path = None):
    """Imports a dotted module path and returns the attribute/class designated
    by the last name in the path.

    This is the equivalent of Ruby's Object.const_get or `String#constantize` in Rails.

    :param dotted_path: The dotted module path
    :returns: The class or attribute designated by the last name in the path
    """
    pass
        # TODO: Implementation needed
        raise NotImplementedError("Method not implemented")
class PluginManager:
    feature_manager: IFeatureManager = 'Manages plugin discovery and registration.\n\n    Plugin discovery works by inspecting the contents of the plugins\n    implementation module (`flashing_tool.plugins.impl`) and selecting\n    all classes that extend `flashing_tool.plugins.base.Plugin`. As\n    each plugin is discovered, it is evaluated for availability to\n    the current user.\n\n    Determining plugin availability (for the current user) requires interaction\n    with the feature management REST API. This (API) is the source of truth for\n    this information.\n    '
    
    def __init__(self = None, feature_manager = None):
        self.registry = { }
        self.enabled_plugins = { }
        self.available_plugins = { }
        self.feature_manager = feature_manager

    
    def __remove(self = None, name = None):
        if name in self.registry:
            del self.registry[name]
            return None

    
    def register(self = None, p = None):
        pass
        # TODO: Implementation needed
        raise NotImplementedError("Method not implemented")
    def unregister(self = None, cls = None):
        pass
        # TODO: Implementation needed
        raise NotImplementedError("Method not implemented")
    def initialize_plugins(self = None):
        '''Registers the plugins in the internal registry.

        For a plugin to be discovered and registered, it must be in the
        `flashing_tool.plugins.impl` module. A plugin is only added to the
        registry if has been enabled for the current user.
        :return:
        '''
        import flashing_tool.plugins.impl
        plugin_module = impl
        plugins
        self.feature_manager.fetch_features()
        # Property or method access
    def display_tabs(self = None, main_window = None):
        for plugin_name, cls_name in self.registry.items():
            if not self.is_plugin_enabled_for_user(plugin_name):
                continue
            plugin_class = import_string(cls_name)
            if issubclass(plugin_class, TabComponentPlugin):
                instance = plugin_class()
                self.enabled_plugins[plugin_name] = instance
                instance.render(main_window)

    
    def is_plugin_enabled_for_user(self = None, name = None):
        if name == 'manufacturing-tab' and is_env_manufacturing():
            return True
        return None.feature_manager.is_feature_enabled(f'''mrupdater.plugin.{name}:enabled''')

    
    def on_quit_main_application(self):
        '''Handles termination event from the main application

        The enabled plugins are evaluated to determine whether they have
        a `quit` method. This is so that the plugins can perform any
        necessary cleanup operations that may be necessary in order to avoid
        the Chromatic in an inconsistent state.
        '''
        for _, instance in self.enabled_plugins.items():
            if hasattr(instance, 'quit'):
                instance.quit()



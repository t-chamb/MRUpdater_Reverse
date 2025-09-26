# Source Generated with Decompyle++
# File: _config.pyc (Python 3.10)

from __future__ import annotations as _annotations
import warnings
from contextlib import contextmanager
from re import Pattern
from typing import TYPE_CHECKING, Any, Callable, Literal, cast
from pydantic_core import core_schema
from typing_extensions import Self
from aliases import AliasGenerator
from config import ConfigDict, ExtraValues, JsonDict, JsonEncoder, JsonSchemaExtraCallable
from errors import PydanticUserError
from warnings import PydanticDeprecatedSince20, PydanticDeprecatedSince210
if not TYPE_CHECKING:
    DeprecationWarning = PydanticDeprecatedSince20
if TYPE_CHECKING:
    from _internal._schema_generation_shared import GenerateSchema
    from fields import ComputedFieldInfo, FieldInfo
DEPRECATION_MESSAGE = 'Support for class-based `config` is deprecated, use ConfigDict instead.'

class ConfigWrapper:
    '''Internal wrapper for Config which exposes ConfigDict items as attributes.'''
    serialize_by_alias: 'bool' = ('config_dict',)
    
    def __init__(self = None, config = None, *, check):
        if check:
            self.config_dict = prepare_config(config)
            return None
        self.config_dict = None(ConfigDict, config)

    
    def for_model(cls = None, bases = None, namespace = classmethod, kwargs = ('bases', 'tuple[type[Any], ...]', 'namespace', 'dict[str, Any]', 'kwargs', 'dict[str, Any]', 'return', 'Self')):
        '''Build a new `ConfigWrapper` instance for a `BaseModel`.

        The config wrapper built based on (in descending order of priority):
        - options from `kwargs`
        - options from the `namespace`
        - options from the base classes (`bases`)

        Args:
            bases: A tuple of base classes.
            namespace: The namespace of the class being created.
            kwargs: The kwargs passed to the class being created.

        Returns:
            A `ConfigWrapper` instance for `BaseModel`.
        '''
        config_new = ConfigDict()
        for base in bases:
            config = getattr(base, 'model_config', None)
            if config:
                config_new.update(config.copy())
        config_class_from_namespace = namespace.get('Config')
        config_dict_from_namespace = namespace.get('model_config')
        raw_annotations = namespace.get('__annotations__', { })
        if raw_annotations.get('model_config') and config_dict_from_namespace is None:
            raise PydanticUserError('`model_config` cannot be used as a model field name. Use `model_config` for model configuration.', 'model-config-invalid-field-name', **('code',))
        if config_class_from_namespace and config_dict_from_namespace:
            raise PydanticUserError('"Config" and "model_config" cannot be used together', 'config-both', **('code',))
        if not config_dict_from_namespace:
            pass
        config_from_namespace = prepare_config(config_class_from_namespace)
        config_new.update(config_from_namespace)
        for k in list(kwargs.keys()):
            if k in config_keys:
                config_new[k] = kwargs.pop(k)
        return cls(config_new)

    for_model = None(for_model)
    if not TYPE_CHECKING:
        
        def __getattr__(self = None, name = None):
            pass
        # WARNING: Decompyle incomplete

    
    def core_config(self = None, title = None):
        """Create a pydantic-core config.

        We don't use getattr here since we don't want to populate with defaults.

        Args:
            title: The title to use if not set in config.

        Returns:
            A `CoreConfig` object created from config.
        """
        config = self.config_dict
        if config.get('schema_generator') is not None:
            warnings.warn('The `schema_generator` setting has been deprecated since v2.10. This setting no longer has any effect.', PydanticDeprecatedSince210, 2, **('stacklevel',))
        if populate_by_name = config.get('populate_by_name') is not None and config.get('validate_by_name') is None:
            config['validate_by_alias'] = True
            config['validate_by_name'] = populate_by_name
        if config.get('validate_by_alias') is False and config.get('validate_by_name') is None:
            config['validate_by_name'] = True
        if not config.get('validate_by_alias', True) and config.get('validate_by_name', False):
            raise PydanticUserError('At least one of `validate_by_alias` or `validate_by_name` must be set to True.', 'validate-by-alias-and-name-false', **('code',))
        if not config.get('title') and title:
            pass
    # WARNING: Decompyle incomplete

    
    def __repr__(self):
        c = ', '.join((lambda .0: for k, v in .0:
f'''{k}={v!r}''')(self.config_dict.items()))
        return f'''ConfigWrapper({c})'''



class ConfigWrapperStack:
    '''A stack of `ConfigWrapper` instances.'''
    
    def __init__(self = None, config_wrapper = None):
        self._config_wrapper_stack = [
            config_wrapper]

    
    def tail(self = None):
        return self._config_wrapper_stack[-1]

    tail = None(tail)
    
    def push(self = None, config_wrapper = None):
        if config_wrapper is None:
            yield None
            return None
        if not None(config_wrapper, ConfigWrapper):
            config_wrapper = ConfigWrapper(config_wrapper, False, **('check',))
        self._config_wrapper_stack.append(config_wrapper)
    # WARNING: Decompyle incomplete

    push = None(push)

# WARNING: Decompyle incomplete

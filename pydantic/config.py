# Source Generated with Decompyle++
# File: config.pyc (Python 3.10)

'''Configuration for Pydantic models.'''
from __future__ import annotations as _annotations
import warnings
from re import Pattern
from typing import TYPE_CHECKING, Any, Callable, Literal, TypeVar, Union, cast, overload
from typing_extensions import TypeAlias, TypedDict, Unpack, deprecated
from _migration import getattr_migration
from aliases import AliasGenerator
from errors import PydanticUserError
from warnings import PydanticDeprecatedSince211
if TYPE_CHECKING:
    from _internal._generate_schema import GenerateSchema as _GenerateSchema
    from fields import ComputedFieldInfo, FieldInfo
__all__ = ('ConfigDict', 'with_config')
JsonValue: 'TypeAlias' = Union[(int, float, str, bool, None, list['JsonValue'], 'JsonDict')]
JsonDict: 'TypeAlias' = dict[(str, JsonValue)]
JsonEncoder = Callable[([
    Any], Any)]
JsonSchemaExtraCallable: 'TypeAlias' = Union[(Callable[([
    JsonDict], None)], Callable[([
    JsonDict,
    type[Any]], None)])]
ExtraValues = Literal[('allow', 'ignore', 'forbid')]
ConfigDict = <NODE:27>((lambda : serialize_by_alias: 'bool' = 'A TypedDict for configuring Pydantic behaviour.'), 'ConfigDict', TypedDict, False, **('total',))
_TypeT = TypeVar('_TypeT', type, **('bound',))

def with_config(*, config):
    pass

with_config = None(None(with_config))

def with_config(config = None):
    pass

with_config = None(with_config)

def with_config(**config):
    pass

with_config = None(with_config)

def with_config(config = None, **kwargs):
    '''!!! abstract "Usage Documentation"
        [Configuration with other types](../concepts/config.md#configuration-on-other-supported-types)

    A convenience decorator to set a [Pydantic configuration](config.md) on a `TypedDict` or a `dataclass` from the standard library.

    Although the configuration can be set using the `__pydantic_config__` attribute, it does not play well with type checkers,
    especially with `TypedDict`.

    !!! example "Usage"

        ```python
        from typing_extensions import TypedDict

        from pydantic import ConfigDict, TypeAdapter, with_config

        @with_config(ConfigDict(str_to_lower=True))
        class TD(TypedDict):
            x: str

        ta = TypeAdapter(TD)

        print(ta.validate_python({\'x\': \'ABC\'}))
        #> {\'x\': \'abc\'}
        ```
    '''
    if config is not None and kwargs:
        raise ValueError('Cannot specify both `config` and keyword arguments')
    if len(kwargs) == 1 and kwargs_conf = kwargs.get('config') is not None:
        warnings.warn('Passing `config` as a keyword argument is deprecated. Pass `config` as a positional argument instead', PydanticDeprecatedSince211, 2, **('category', 'stacklevel'))
        final_config = cast(ConfigDict, kwargs_conf)
    elif config is not None:
        pass
    
    final_config = cast(ConfigDict, kwargs)
    
    def inner(class_ = None):
        is_model_class = is_model_class
        import _internal._utils
        if is_model_class(class_):
            raise PydanticUserError(f'''Cannot use `with_config` on {class_.__name__} as it is a Pydantic model''', 'with-config-on-model', **('code',))
        class_.__pydantic_config__ = final_config
        return class_

    return inner

__getattr__ = getattr_migration(__name__)

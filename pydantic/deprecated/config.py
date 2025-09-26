# Source Generated with Decompyle++
# File: config.pyc (Python 3.10)

from __future__ import annotations as _annotations
import warnings
from typing import TYPE_CHECKING, Any, Literal
from typing_extensions import deprecated
from _internal import _config
from warnings import PydanticDeprecatedSince20
if not TYPE_CHECKING:
    DeprecationWarning = PydanticDeprecatedSince20
__all__ = ('BaseConfig', 'Extra')

class _ConfigMetaclass(type):
    
    def __getattr__(self = None, item = None):
        pass
    # WARNING: Decompyle incomplete


BaseConfig = deprecated('BaseConfig is deprecated. Use the `pydantic.ConfigDict` instead.', PydanticDeprecatedSince20, **('category',))(<NODE:27>((lambda : __doc__ = 'This class is only retained for backwards compatibility.\n\n    !!! Warning "Deprecated"\n        BaseConfig is deprecated. Use the [`pydantic.ConfigDict`][pydantic.ConfigDict] instead.\n    '
def __getattr__(self = None, item = None):
pass# WARNING: Decompyle incomplete

def __init_subclass__(cls = None, **kwargs):
warnings.warn(_config.DEPRECATION_MESSAGE, DeprecationWarning)# WARNING: Decompyle incomplete
__classcell__ = None), 'BaseConfig', _ConfigMetaclass, **('metaclass',)))

class _ExtraMeta(type):
    
    def __getattribute__(self = None, _ExtraMeta__name = None):
        if _ExtraMeta__name in frozenset({'ignore', 'forbid', 'allow'}):
            warnings.warn("`pydantic.config.Extra` is deprecated, use literal values instead (e.g. `extra='allow'`)", DeprecationWarning, 2, **('stacklevel',))
        return super().__getattribute__(_ExtraMeta__name)

    __classcell__ = None

Extra = deprecated("Extra is deprecated. Use literal values instead (e.g. `extra='allow'`)", PydanticDeprecatedSince20, **('category',))(<NODE:27>((lambda : allow: "Literal['allow']" = 'allow'ignore: "Literal['ignore']" = 'ignore'forbid: "Literal['forbid']" = 'forbid'), 'Extra', _ExtraMeta, **('metaclass',)))

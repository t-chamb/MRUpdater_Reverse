# Source Generated with Decompyle++
# File: config.pyc (Python 3.10)

import json
from enum import Enum
from typing import TYPE_CHECKING, Any, Callable, Dict, ForwardRef, Optional, Tuple, Type, Union
from typing_extensions import Literal, Protocol
from pydantic.v1.typing import AnyArgTCallable, AnyCallable
from pydantic.v1.utils import GetterDict
from pydantic.v1.version import compiled
if TYPE_CHECKING:
    from typing import overload
    from pydantic.v1.fields import ModelField
    from pydantic.v1.main import BaseModel
    ConfigType = Type['BaseConfig']
    
    class SchemaExtraCallable(Protocol):
        
        def __call__(self = None, schema = None):
            pass

        __call__ = None(__call__)
        
        def __call__(self = None, schema = None, model_class = overload):
            pass

        __call__ = None(__call__)

else:
    SchemaExtraCallable = Callable[(..., None)]
__all__ = ('BaseConfig', 'ConfigDict', 'get_config', 'Extra', 'inherit_config', 'prepare_config')

class Extra(Enum, str):
    allow = 'allow'
    ignore = 'ignore'
    forbid = 'forbid'

if not compiled:
    from typing_extensions import TypedDict
    ConfigDict = <NODE:27>((lambda : post_init_call: Literal[('before_validation', 'after_validation')] = 'ConfigDict'), 'ConfigDict', TypedDict, False, **('total',))
else:
    ConfigDict = dict

class BaseConfig:
    title: Optional[str] = None
    anystr_lower: bool = False
    anystr_upper: bool = False
    anystr_strip_whitespace: bool = False
    min_anystr_length: int = 0
    max_anystr_length: Optional[int] = None
    validate_all: bool = False
    extra: Extra = Extra.ignore
    allow_mutation: bool = True
    frozen: bool = False
    allow_population_by_field_name: bool = False
    use_enum_values: bool = False
    fields: Dict[(str, Union[(str, Dict[(str, str)])])] = { }
    validate_assignment: bool = False
    error_msg_templates: Dict[(str, str)] = { }
    arbitrary_types_allowed: bool = False
    orm_mode: bool = False
    getter_dict: Type[GetterDict] = GetterDict
    alias_generator: Optional[Callable[([
        str], str)]] = None
    keep_untouched: Tuple[(type, ...)] = ()
    schema_extra: Union[(Dict[(str, Any)], 'SchemaExtraCallable')] = { }
    json_loads: Callable[([
        str], Any)] = json.loads
    json_dumps: Callable[(..., str)] = json.dumps
    json_encoders: Dict[(Union[(Type[Any], str, ForwardRef)], AnyCallable)] = { }
    underscore_attrs_are_private: bool = False
    allow_inf_nan: bool = True
    copy_on_model_validation: Literal[('none', 'deep', 'shallow')] = 'shallow'
    smart_union: bool = False
    post_init_call: Literal[('before_validation', 'after_validation')] = 'before_validation'
    
    def get_field_info(cls = None, name = None):
        '''
        Get properties of FieldInfo from the `fields` property of the config class.
        '''
        fields_value = cls.fields.get(name)
        if isinstance(fields_value, str):
            field_info = {
                'alias': fields_value }
        elif isinstance(fields_value, dict):
            field_info = fields_value
        else:
            field_info = { }
        if 'alias' in field_info:
            field_info.setdefault('alias_priority', 2)
        if field_info.get('alias_priority', 0) <= 1 and cls.alias_generator:
            alias = cls.alias_generator(name)
            if not isinstance(alias, str):
                raise TypeError(f'''Config.alias_generator must return str, not {alias.__class__}''')
            field_info.update(alias, 1, **('alias', 'alias_priority'))
        return field_info

    get_field_info = None(get_field_info)
    
    def prepare_field(cls = None, field = None):
        '''
        Optional hook to check or modify fields during model creation.
        '''
        pass

    prepare_field = None(prepare_field)


def get_config(config = None):
    if config is None:
        return BaseConfig
    config_dict = None if None(config, dict) else (lambda .0 = None: pass# WARNING: Decompyle incomplete
)(dir(config))
    
    class Config(BaseConfig):
        pass

    for k, v in config_dict.items():
        setattr(Config, k, v)
    return Config


def inherit_config(self_config = None, parent_config = None, **namespace):
    if not self_config:
        base_classes = (parent_config,)
    elif self_config == parent_config:
        base_classes = (self_config,)
    else:
        base_classes = (self_config, parent_config)
# WARNING: Decompyle incomplete


def prepare_config(config = None, cls_name = None):
    pass
# WARNING: Decompyle incomplete


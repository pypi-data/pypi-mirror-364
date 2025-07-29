"""JSON adapter module to replace orjson with standard library json."""

import json
from typing import Any, Union


# orjson option constants compatibility
OPT_SORT_KEYS = 1  # Simulate orjson.OPT_SORT_KEYS


def loads(json_str: Union[str, bytes]) -> Any:
    """
    Load JSON from string or bytes, compatible with orjson.loads().
    
    Args:
        json_str: JSON string or bytes to parse
        
    Returns:
        Parsed JSON object
    """
    if isinstance(json_str, bytes):
        json_str = json_str.decode('utf-8')
    return json.loads(json_str)


def dumps(obj: Any, option: int = 0) -> bytes:
    """
    Dump object to JSON bytes, compatible with orjson.dumps().
    
    Args:
        obj: Object to serialize
        option: Options (only OPT_SORT_KEYS is supported)
        
    Returns:
        JSON as bytes
    """
    kwargs = {}
    if option & OPT_SORT_KEYS:
        kwargs['sort_keys'] = True
    
    # Standard json always returns str, so we encode to bytes for orjson compatibility
    json_str = json.dumps(obj, ensure_ascii=False, separators=(',', ':'), **kwargs)
    return json_str.encode('utf-8')


# For backwards compatibility, create a module-like structure
class OrjsonCompat:
    """Compatibility layer for orjson module."""
    OPT_SORT_KEYS = OPT_SORT_KEYS
    loads = staticmethod(loads)
    dumps = staticmethod(dumps)


# Default export
orjson_compat = OrjsonCompat()

import re
from collections.abc import Mapping
from typing import Union, Dict, List

SPLIT_RE = re.compile(r"([\-_\s]*[A-Z0-9]+[^A-Z\-_\s]+[\-_\s]*)")
ACRONYM_RE = re.compile(r"([A-Z]+)(?=[A-Z][a-z])")


def to_snake_case(str_or_iter: Union[str, Dict, List]):
    """Convert a string, dict, or list of dicts to snake case"""
    if isinstance(str_or_iter, (list, Mapping)):
        return _process_keys(str_or_iter, to_snake_case)

    s = str(str_or_iter)
    if s.isnumeric():
        return str_or_iter

    if s.isupper():
        return str_or_iter

    return _break_words(_fix_abbrevations(s)).lower()


def _break_words(string: str, separator: str = "_", split=SPLIT_RE.split):
    return separator.join(s for s in split(string) if s)


def _fix_abbrevations(string: str) -> str:
    """Fix acronyms, initialisms, and abbrevations, e.g. `ObjectID` should
    be `object_id` not `object_i_d`
    """
    return ACRONYM_RE.sub(lambda m: m.group(0).title(), string)


def _process_keys(str_or_iter, fn):
    if isinstance(str_or_iter, list):
        return [_process_keys(k, fn) for k in str_or_iter]
    elif isinstance(str_or_iter, Mapping):
        return {fn(k): _process_keys(v, fn) for k, v in str_or_iter.items()}
    else:
        return str_or_iter

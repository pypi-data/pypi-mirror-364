"""
Model wrappers that forward to implementations in ``nlpkit._core``.
"""
from importlib import import_module as _imp

_core = _imp("nlpkit._core")

# expose everything that starts with an uppercase letter and isn't private
for _name in dir(_core):
    if _name.startswith("_"):
        continue
    _obj = getattr(_core, _name)
    if isinstance(_obj, type):
        globals()[_name] = _obj
        __all__.append(_name)

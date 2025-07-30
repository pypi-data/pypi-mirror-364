try:
    import orjson as complexjson
except ImportError:
    import json as complexjson
from .enums import *
from .objects import *
from .funcs import *

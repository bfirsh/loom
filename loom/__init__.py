VERSION = (0, 0, 10)
__version__ = ".".join([str(x) for x in VERSION])

# ensure env variables are set first before overrides
from . import config


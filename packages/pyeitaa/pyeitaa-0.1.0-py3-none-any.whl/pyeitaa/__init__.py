__version__ = "0.1.0"
__copyright__ = "Copyright (C) 2025-present MSDanesh <https://github.com/MSDanesh>"


class StopTransmission(Exception):
    pass


from . import raw, types, enums
from .client import Client
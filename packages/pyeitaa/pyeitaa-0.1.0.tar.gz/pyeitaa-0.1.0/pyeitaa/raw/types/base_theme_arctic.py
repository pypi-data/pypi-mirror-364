from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class BaseThemeArctic(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.BaseTheme`.

    Details:
        - Layer: ``135``
        - ID: ``0x5b11125a``

    **No parameters required.**
    """

    __slots__: List[str] = []

    ID = 0x5b11125a
    QUALNAME = "types.BaseThemeArctic"

    def __init__(self) -> None:
        pass

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        return BaseThemeArctic()

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        return data.getvalue()

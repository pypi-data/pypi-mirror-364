from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class BaseThemeNight(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.BaseTheme`.

    Details:
        - Layer: ``135``
        - ID: ``-0x484ce158``

    **No parameters required.**
    """

    __slots__: List[str] = []

    ID = -0x484ce158
    QUALNAME = "types.BaseThemeNight"

    def __init__(self) -> None:
        pass

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        return BaseThemeNight()

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        return data.getvalue()

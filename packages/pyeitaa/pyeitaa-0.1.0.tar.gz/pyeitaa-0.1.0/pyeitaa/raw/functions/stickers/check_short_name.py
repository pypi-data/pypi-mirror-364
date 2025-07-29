from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class CheckShortName(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x284b3639``

    Parameters:
        short_name: ``str``

    Returns:
        ``bool``
    """

    __slots__: List[str] = ["short_name"]

    ID = 0x284b3639
    QUALNAME = "functions.stickers.CheckShortName"

    def __init__(self, *, short_name: str) -> None:
        self.short_name = short_name  # string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        short_name = String.read(data)
        
        return CheckShortName(short_name=short_name)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(String(self.short_name))
        
        return data.getvalue()

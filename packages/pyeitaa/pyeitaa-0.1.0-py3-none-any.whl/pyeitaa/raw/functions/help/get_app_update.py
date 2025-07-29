from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class GetAppUpdate(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x522d5a7d``

    Parameters:
        source: ``str``

    Returns:
        :obj:`help.AppUpdate <pyeitaa.raw.base.help.AppUpdate>`
    """

    __slots__: List[str] = ["source"]

    ID = 0x522d5a7d
    QUALNAME = "functions.help.GetAppUpdate"

    def __init__(self, *, source: str) -> None:
        self.source = source  # string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        source = String.read(data)
        
        return GetAppUpdate(source=source)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(String(self.source))
        
        return data.getvalue()

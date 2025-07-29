from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, String
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class GetThemes(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x7206e458``

    Parameters:
        format: ``str``
        hash: ``int`` ``64-bit``

    Returns:
        :obj:`account.Themes <pyeitaa.raw.base.account.Themes>`
    """

    __slots__: List[str] = ["format", "hash"]

    ID = 0x7206e458
    QUALNAME = "functions.account.GetThemes"

    def __init__(self, *, format: str, hash: int) -> None:
        self.format = format  # string
        self.hash = hash  # long

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        format = String.read(data)
        
        hash = Long.read(data)
        
        return GetThemes(format=format, hash=hash)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(String(self.format))
        
        data.write(Long(self.hash))
        
        return data.getvalue()

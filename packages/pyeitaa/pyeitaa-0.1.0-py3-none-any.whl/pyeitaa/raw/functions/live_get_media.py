from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class LiveGetMedia(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x4731a7ba``

    Parameters:
        id: ``int`` ``64-bit``
        access_hash: ``int`` ``64-bit``

    Returns:
        :obj:`LiveGetMedia <pyeitaa.raw.base.LiveGetMedia>`
    """

    __slots__: List[str] = ["id", "access_hash"]

    ID = 0x4731a7ba
    QUALNAME = "functions.LiveGetMedia"

    def __init__(self, *, id: int, access_hash: int) -> None:
        self.id = id  # long
        self.access_hash = access_hash  # long

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        id = Long.read(data)
        
        access_hash = Long.read(data)
        
        return LiveGetMedia(id=id, access_hash=access_hash)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        
        data.write(Int(flags))
        
        data.write(Long(self.id))
        
        data.write(Long(self.access_hash))
        
        return data.getvalue()

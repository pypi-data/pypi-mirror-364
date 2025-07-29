from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long
from pyeitaa.raw.core import TLObject
from typing import List, Optional, Any, Self


class GetRecentStickers(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x6256bfc5``

    Parameters:
        hash: ``int`` ``64-bit``
        attached (optional): ``bool``

    Returns:
        :obj:`messages.RecentStickers <pyeitaa.raw.base.messages.RecentStickers>`
    """

    __slots__: List[str] = ["hash", "attached"]

    ID = -0x6256bfc5
    QUALNAME = "functions.messages.GetRecentStickers"

    def __init__(self, *, hash: int, attached: Optional[bool] = None) -> None:
        self.hash = hash  # long
        self.attached = attached  # flags.0?true

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        attached = True if flags & (1 << 0) else False
        hash = Long.read(data)
        
        return GetRecentStickers(hash=hash, attached=attached)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.attached else 0
        data.write(Int(flags))
        
        data.write(Long(self.hash))
        
        return data.getvalue()

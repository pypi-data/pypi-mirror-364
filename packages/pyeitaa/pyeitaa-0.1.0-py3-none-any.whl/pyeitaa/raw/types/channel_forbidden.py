from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, String
from pyeitaa.raw.core import TLObject
from typing import List, Optional, Any, Self


class ChannelForbidden(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.Chat`.

    Details:
        - Layer: ``135``
        - ID: ``0x17d493d5``

    Parameters:
        id: ``int`` ``64-bit``
        access_hash: ``int`` ``64-bit``
        title: ``str``
        broadcast (optional): ``bool``
        megagroup (optional): ``bool``
        until_date (optional): ``int`` ``32-bit``
    """

    __slots__: List[str] = ["id", "access_hash", "title", "broadcast", "megagroup", "until_date"]

    ID = 0x17d493d5
    QUALNAME = "types.ChannelForbidden"

    def __init__(self, *, id: int, access_hash: int, title: str, broadcast: Optional[bool] = None, megagroup: Optional[bool] = None, until_date: Optional[int] = None) -> None:
        self.id = id  # long
        self.access_hash = access_hash  # long
        self.title = title  # string
        self.broadcast = broadcast  # flags.5?true
        self.megagroup = megagroup  # flags.8?true
        self.until_date = until_date  # flags.16?int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        broadcast = True if flags & (1 << 5) else False
        megagroup = True if flags & (1 << 8) else False
        id = Long.read(data)
        
        access_hash = Long.read(data)
        
        title = String.read(data)
        
        until_date = Int.read(data) if flags & (1 << 16) else None
        return ChannelForbidden(id=id, access_hash=access_hash, title=title, broadcast=broadcast, megagroup=megagroup, until_date=until_date)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 5) if self.broadcast else 0
        flags |= (1 << 8) if self.megagroup else 0
        flags |= (1 << 16) if self.until_date is not None else 0
        data.write(Int(flags))
        
        data.write(Long(self.id))
        
        data.write(Long(self.access_hash))
        
        data.write(String(self.title))
        
        if self.until_date is not None:
            data.write(Int(self.until_date))
        
        return data.getvalue()

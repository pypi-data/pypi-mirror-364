from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from typing import List, Optional, Any, Self


class LiveStreamStateEnded(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.LiveStreamState`.

    Details:
        - Layer: ``135``
        - ID: ``-0x47b2ea55``

    Parameters:
        duration: ``int`` ``32-bit``
        expire_date (optional): ``int`` ``32-bit``
        archive_link (optional): ``str``
    """

    __slots__: List[str] = ["duration", "expire_date", "archive_link"]

    ID = -0x47b2ea55
    QUALNAME = "types.LiveStreamStateEnded"

    def __init__(self, *, duration: int, expire_date: Optional[int] = None, archive_link: Optional[str] = None) -> None:
        self.duration = duration  # int
        self.expire_date = expire_date  # flags.0?int
        self.archive_link = archive_link  # flags.0?string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        duration = Int.read(data)
        
        expire_date = Int.read(data) if flags & (1 << 0) else None
        archive_link = String.read(data) if flags & (1 << 0) else None
        return LiveStreamStateEnded(duration=duration, expire_date=expire_date, archive_link=archive_link)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.expire_date is not None else 0
        flags |= (1 << 0) if self.archive_link is not None else 0
        data.write(Int(flags))
        
        data.write(Int(self.duration))
        
        if self.expire_date is not None:
            data.write(Int(self.expire_date))
        
        if self.archive_link is not None:
            data.write(String(self.archive_link))
        
        return data.getvalue()

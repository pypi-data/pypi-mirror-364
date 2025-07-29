from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from typing import List, Optional, Any, Self


class LiveStreamStateEnded2(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.LiveStreamState`.

    Details:
        - Layer: ``135``
        - ID: ``-0x32f3e52``

    Parameters:
        duration: ``int`` ``32-bit``
        expire_date (optional): ``int`` ``32-bit``
        archive_link (optional): ``str``
        archive_size (optional): ``int`` ``32-bit``
    """

    __slots__: List[str] = ["duration", "expire_date", "archive_link", "archive_size"]

    ID = -0x32f3e52
    QUALNAME = "types.LiveStreamStateEnded2"

    def __init__(self, *, duration: int, expire_date: Optional[int] = None, archive_link: Optional[str] = None, archive_size: Optional[int] = None) -> None:
        self.duration = duration  # int
        self.expire_date = expire_date  # flags.0?int
        self.archive_link = archive_link  # flags.0?string
        self.archive_size = archive_size  # flags.0?int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        duration = Int.read(data)
        
        expire_date = Int.read(data) if flags & (1 << 0) else None
        archive_link = String.read(data) if flags & (1 << 0) else None
        archive_size = Int.read(data) if flags & (1 << 0) else None
        return LiveStreamStateEnded2(duration=duration, expire_date=expire_date, archive_link=archive_link, archive_size=archive_size)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.expire_date is not None else 0
        flags |= (1 << 0) if self.archive_link is not None else 0
        flags |= (1 << 0) if self.archive_size is not None else 0
        data.write(Int(flags))
        
        data.write(Int(self.duration))
        
        if self.expire_date is not None:
            data.write(Int(self.expire_date))
        
        if self.archive_link is not None:
            data.write(String(self.archive_link))
        
        if self.archive_size is not None:
            data.write(Int(self.archive_size))
        
        return data.getvalue()

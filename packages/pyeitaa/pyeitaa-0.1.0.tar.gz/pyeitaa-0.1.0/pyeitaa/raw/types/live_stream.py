from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from typing import List, Optional, Any, Self


class LiveStream(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.LiveStream`.

    Details:
        - Layer: ``135``
        - ID: ``0x2da75aab``

    Parameters:
        start_date: ``int`` ``32-bit``
        read_link (optional): ``str``
        write_link (optional): ``str``
    """

    __slots__: List[str] = ["start_date", "read_link", "write_link"]

    ID = 0x2da75aab
    QUALNAME = "types.LiveStream"

    def __init__(self, *, start_date: int, read_link: Optional[str] = None, write_link: Optional[str] = None) -> None:
        self.start_date = start_date  # int
        self.read_link = read_link  # flags.0?string
        self.write_link = write_link  # flags.1?string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        read_link = String.read(data) if flags & (1 << 0) else None
        write_link = String.read(data) if flags & (1 << 1) else None
        start_date = Int.read(data)
        
        return LiveStream(start_date=start_date, read_link=read_link, write_link=write_link)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.read_link is not None else 0
        flags |= (1 << 1) if self.write_link is not None else 0
        data.write(Int(flags))
        
        if self.read_link is not None:
            data.write(String(self.read_link))
        
        if self.write_link is not None:
            data.write(String(self.write_link))
        
        data.write(Int(self.start_date))
        
        return data.getvalue()

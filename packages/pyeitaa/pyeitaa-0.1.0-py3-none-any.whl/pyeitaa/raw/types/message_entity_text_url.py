from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class MessageEntityTextUrl(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.MessageEntity`.

    Details:
        - Layer: ``135``
        - ID: ``0x76a6d327``

    Parameters:
        offset: ``int`` ``32-bit``
        length: ``int`` ``32-bit``
        url: ``str``
    """

    __slots__: List[str] = ["offset", "length", "url"]

    ID = 0x76a6d327
    QUALNAME = "types.MessageEntityTextUrl"

    def __init__(self, *, offset: int, length: int, url: str) -> None:
        self.offset = offset  # int
        self.length = length  # int
        self.url = url  # string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        offset = Int.read(data)
        
        length = Int.read(data)
        
        url = String.read(data)
        
        return MessageEntityTextUrl(offset=offset, length=length, url=url)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Int(self.offset))
        
        data.write(Int(self.length))
        
        data.write(String(self.url))
        
        return data.getvalue()

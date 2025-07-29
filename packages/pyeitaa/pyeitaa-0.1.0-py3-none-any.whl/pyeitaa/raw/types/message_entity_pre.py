from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class MessageEntityPre(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.MessageEntity`.

    Details:
        - Layer: ``135``
        - ID: ``0x73924be0``

    Parameters:
        offset: ``int`` ``32-bit``
        length: ``int`` ``32-bit``
        language: ``str``
    """

    __slots__: List[str] = ["offset", "length", "language"]

    ID = 0x73924be0
    QUALNAME = "types.MessageEntityPre"

    def __init__(self, *, offset: int, length: int, language: str) -> None:
        self.offset = offset  # int
        self.length = length  # int
        self.language = language  # string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        offset = Int.read(data)
        
        length = Int.read(data)
        
        language = String.read(data)
        
        return MessageEntityPre(offset=offset, length=length, language=language)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Int(self.offset))
        
        data.write(Int(self.length))
        
        data.write(String(self.language))
        
        return data.getvalue()

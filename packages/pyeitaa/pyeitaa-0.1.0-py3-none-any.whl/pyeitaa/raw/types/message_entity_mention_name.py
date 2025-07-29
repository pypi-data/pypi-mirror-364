from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class MessageEntityMentionName(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.MessageEntity`.

    Details:
        - Layer: ``135``
        - ID: ``-0x2384eec0``

    Parameters:
        offset: ``int`` ``32-bit``
        length: ``int`` ``32-bit``
        user_id: ``int`` ``64-bit``
    """

    __slots__: List[str] = ["offset", "length", "user_id"]

    ID = -0x2384eec0
    QUALNAME = "types.MessageEntityMentionName"

    def __init__(self, *, offset: int, length: int, user_id: int) -> None:
        self.offset = offset  # int
        self.length = length  # int
        self.user_id = user_id  # long

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        offset = Int.read(data)
        
        length = Int.read(data)
        
        user_id = Long.read(data)
        
        return MessageEntityMentionName(offset=offset, length=length, user_id=user_id)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Int(self.offset))
        
        data.write(Int(self.length))
        
        data.write(Long(self.user_id))
        
        return data.getvalue()

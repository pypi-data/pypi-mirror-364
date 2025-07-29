from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class InputMessageEntityMentionName(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.MessageEntity`.

    Details:
        - Layer: ``135``
        - ID: ``0x208e68c9``

    Parameters:
        offset: ``int`` ``32-bit``
        length: ``int`` ``32-bit``
        user_id: :obj:`InputUser <pyeitaa.raw.base.InputUser>`
    """

    __slots__: List[str] = ["offset", "length", "user_id"]

    ID = 0x208e68c9
    QUALNAME = "types.InputMessageEntityMentionName"

    def __init__(self, *, offset: int, length: int, user_id: "raw.base.InputUser") -> None:
        self.offset = offset  # int
        self.length = length  # int
        self.user_id = user_id  # InputUser

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        offset = Int.read(data)
        
        length = Int.read(data)
        
        user_id = TLObject.read(data)
        
        return InputMessageEntityMentionName(offset=offset, length=length, user_id=user_id)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Int(self.offset))
        
        data.write(Int(self.length))
        
        data.write(self.user_id.write())
        
        return data.getvalue()

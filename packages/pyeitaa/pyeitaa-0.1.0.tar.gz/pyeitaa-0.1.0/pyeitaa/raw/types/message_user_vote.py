from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, Bytes
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class MessageUserVote(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.MessageUserVote`.

    Details:
        - Layer: ``135``
        - ID: ``0x34d247b4``

    Parameters:
        user_id: ``int`` ``64-bit``
        option: ``bytes``
        date: ``int`` ``32-bit``
    """

    __slots__: List[str] = ["user_id", "option", "date"]

    ID = 0x34d247b4
    QUALNAME = "types.MessageUserVote"

    def __init__(self, *, user_id: int, option: bytes, date: int) -> None:
        self.user_id = user_id  # long
        self.option = option  # bytes
        self.date = date  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        user_id = Long.read(data)
        
        option = Bytes.read(data)
        
        date = Int.read(data)
        
        return MessageUserVote(user_id=user_id, option=option, date=date)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Long(self.user_id))
        
        data.write(Bytes(self.option))
        
        data.write(Int(self.date))
        
        return data.getvalue()

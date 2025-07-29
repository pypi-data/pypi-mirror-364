from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class ChatParticipant(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.ChatParticipant`.

    Details:
        - Layer: ``135``
        - ID: ``-0x3fd2bff9``

    Parameters:
        user_id: ``int`` ``64-bit``
        inviter_id: ``int`` ``64-bit``
        date: ``int`` ``32-bit``
    """

    __slots__: List[str] = ["user_id", "inviter_id", "date"]

    ID = -0x3fd2bff9
    QUALNAME = "types.ChatParticipant"

    def __init__(self, *, user_id: int, inviter_id: int, date: int) -> None:
        self.user_id = user_id  # long
        self.inviter_id = inviter_id  # long
        self.date = date  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        user_id = Long.read(data)
        
        inviter_id = Long.read(data)
        
        date = Int.read(data)
        
        return ChatParticipant(user_id=user_id, inviter_id=inviter_id, date=date)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Long(self.user_id))
        
        data.write(Long(self.inviter_id))
        
        data.write(Int(self.date))
        
        return data.getvalue()

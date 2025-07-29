from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class MessageUserVoteInputOption(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.MessageUserVote`.

    Details:
        - Layer: ``135``
        - ID: ``0x3ca5b0ec``

    Parameters:
        user_id: ``int`` ``64-bit``
        date: ``int`` ``32-bit``
    """

    __slots__: List[str] = ["user_id", "date"]

    ID = 0x3ca5b0ec
    QUALNAME = "types.MessageUserVoteInputOption"

    def __init__(self, *, user_id: int, date: int) -> None:
        self.user_id = user_id  # long
        self.date = date  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        user_id = Long.read(data)
        
        date = Int.read(data)
        
        return MessageUserVoteInputOption(user_id=user_id, date=date)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Long(self.user_id))
        
        data.write(Int(self.date))
        
        return data.getvalue()

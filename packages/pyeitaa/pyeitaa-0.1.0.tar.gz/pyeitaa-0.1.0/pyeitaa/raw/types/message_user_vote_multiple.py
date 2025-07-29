from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, Bytes, Vector
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class MessageUserVoteMultiple(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.MessageUserVote`.

    Details:
        - Layer: ``135``
        - ID: ``-0x759a1aa9``

    Parameters:
        user_id: ``int`` ``64-bit``
        options: List of ``bytes``
        date: ``int`` ``32-bit``
    """

    __slots__: List[str] = ["user_id", "options", "date"]

    ID = -0x759a1aa9
    QUALNAME = "types.MessageUserVoteMultiple"

    def __init__(self, *, user_id: int, options: List[bytes], date: int) -> None:
        self.user_id = user_id  # long
        self.options = options  # Vector<bytes>
        self.date = date  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        user_id = Long.read(data)
        
        options = TLObject.read(data, Bytes)
        
        date = Int.read(data)
        
        return MessageUserVoteMultiple(user_id=user_id, options=options, date=date)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Long(self.user_id))
        
        data.write(Vector(self.options, Bytes))
        
        data.write(Int(self.date))
        
        return data.getvalue()

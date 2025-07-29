from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, Bytes, Vector
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class UpdateMessagePollVote(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.Update`.

    Details:
        - Layer: ``135``
        - ID: ``0x106395c9``

    Parameters:
        poll_id: ``int`` ``64-bit``
        user_id: ``int`` ``64-bit``
        options: List of ``bytes``
        qts: ``int`` ``32-bit``
    """

    __slots__: List[str] = ["poll_id", "user_id", "options", "qts"]

    ID = 0x106395c9
    QUALNAME = "types.UpdateMessagePollVote"

    def __init__(self, *, poll_id: int, user_id: int, options: List[bytes], qts: int) -> None:
        self.poll_id = poll_id  # long
        self.user_id = user_id  # long
        self.options = options  # Vector<bytes>
        self.qts = qts  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        poll_id = Long.read(data)
        
        user_id = Long.read(data)
        
        options = TLObject.read(data, Bytes)
        
        qts = Int.read(data)
        
        return UpdateMessagePollVote(poll_id=poll_id, user_id=user_id, options=options, qts=qts)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Long(self.poll_id))
        
        data.write(Long(self.user_id))
        
        data.write(Vector(self.options, Bytes))
        
        data.write(Int(self.qts))
        
        return data.getvalue()

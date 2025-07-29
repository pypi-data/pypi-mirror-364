from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class MsgDetailedInfo(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.MsgDetailedInfo`.

    Details:
        - Layer: ``135``
        - ID: ``0x276d3ec6``

    Parameters:
        msg_id: ``int`` ``64-bit``
        answer_msg_id: ``int`` ``64-bit``
        bytes: ``int`` ``32-bit``
        status: ``int`` ``32-bit``
    """

    __slots__: List[str] = ["msg_id", "answer_msg_id", "bytes", "status"]

    ID = 0x276d3ec6
    QUALNAME = "types.MsgDetailedInfo"

    def __init__(self, *, msg_id: int, answer_msg_id: int, bytes: int, status: int) -> None:
        self.msg_id = msg_id  # long
        self.answer_msg_id = answer_msg_id  # long
        self.bytes = bytes  # int
        self.status = status  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        msg_id = Long.read(data)
        
        answer_msg_id = Long.read(data)
        
        bytes = Int.read(data)
        
        status = Int.read(data)
        
        return MsgDetailedInfo(msg_id=msg_id, answer_msg_id=answer_msg_id, bytes=bytes, status=status)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Long(self.msg_id))
        
        data.write(Long(self.answer_msg_id))
        
        data.write(Int(self.bytes))
        
        data.write(Int(self.status))
        
        return data.getvalue()

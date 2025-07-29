from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class MsgNewDetailedInfo(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.MsgDetailedInfo`.

    Details:
        - Layer: ``135``
        - ID: ``-0x7f624921``

    Parameters:
        answer_msg_id: ``int`` ``64-bit``
        bytes: ``int`` ``32-bit``
        status: ``int`` ``32-bit``
    """

    __slots__: List[str] = ["answer_msg_id", "bytes", "status"]

    ID = -0x7f624921
    QUALNAME = "types.MsgNewDetailedInfo"

    def __init__(self, *, answer_msg_id: int, bytes: int, status: int) -> None:
        self.answer_msg_id = answer_msg_id  # long
        self.bytes = bytes  # int
        self.status = status  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        answer_msg_id = Long.read(data)
        
        bytes = Int.read(data)
        
        status = Int.read(data)
        
        return MsgNewDetailedInfo(answer_msg_id=answer_msg_id, bytes=bytes, status=status)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Long(self.answer_msg_id))
        
        data.write(Int(self.bytes))
        
        data.write(Int(self.status))
        
        return data.getvalue()

from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, Vector
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class MsgsAck(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.MsgsAck`.

    Details:
        - Layer: ``135``
        - ID: ``0x62d6b459``

    Parameters:
        msg_ids: List of ``int`` ``64-bit``
    """

    __slots__: List[str] = ["msg_ids"]

    ID = 0x62d6b459
    QUALNAME = "types.MsgsAck"

    def __init__(self, *, msg_ids: List[int]) -> None:
        self.msg_ids = msg_ids  # Vector<long>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        msg_ids = TLObject.read(data, Long)
        
        return MsgsAck(msg_ids=msg_ids)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Vector(self.msg_ids, Long))
        
        return data.getvalue()

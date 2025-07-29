from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Vector
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class AffectedFoundMessages(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.messages.AffectedFoundMessages`.

    Details:
        - Layer: ``135``
        - ID: ``-0x1072c194``

    Parameters:
        pts: ``int`` ``32-bit``
        pts_count: ``int`` ``32-bit``
        offset: ``int`` ``32-bit``
        messages: List of ``int`` ``32-bit``

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`messages.DeletePhoneCallHistory <pyeitaa.raw.functions.messages.DeletePhoneCallHistory>`
    """

    __slots__: List[str] = ["pts", "pts_count", "offset", "messages"]

    ID = -0x1072c194
    QUALNAME = "types.messages.AffectedFoundMessages"

    def __init__(self, *, pts: int, pts_count: int, offset: int, messages: List[int]) -> None:
        self.pts = pts  # int
        self.pts_count = pts_count  # int
        self.offset = offset  # int
        self.messages = messages  # Vector<int>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        pts = Int.read(data)
        
        pts_count = Int.read(data)
        
        offset = Int.read(data)
        
        messages = TLObject.read(data, Int)
        
        return AffectedFoundMessages(pts=pts, pts_count=pts_count, offset=offset, messages=messages)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Int(self.pts))
        
        data.write(Int(self.pts_count))
        
        data.write(Int(self.offset))
        
        data.write(Vector(self.messages, Int))
        
        return data.getvalue()

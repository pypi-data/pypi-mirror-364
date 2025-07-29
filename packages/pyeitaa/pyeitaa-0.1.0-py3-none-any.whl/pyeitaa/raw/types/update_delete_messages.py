from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Vector
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class UpdateDeleteMessages(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.Update`.

    Details:
        - Layer: ``135``
        - ID: ``-0x5df24f1b``

    Parameters:
        messages: List of ``int`` ``32-bit``
        pts: ``int`` ``32-bit``
        pts_count: ``int`` ``32-bit``
    """

    __slots__: List[str] = ["messages", "pts", "pts_count"]

    ID = -0x5df24f1b
    QUALNAME = "types.UpdateDeleteMessages"

    def __init__(self, *, messages: List[int], pts: int, pts_count: int) -> None:
        self.messages = messages  # Vector<int>
        self.pts = pts  # int
        self.pts_count = pts_count  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        messages = TLObject.read(data, Int)
        
        pts = Int.read(data)
        
        pts_count = Int.read(data)
        
        return UpdateDeleteMessages(messages=messages, pts=pts, pts_count=pts_count)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Vector(self.messages, Int))
        
        data.write(Int(self.pts))
        
        data.write(Int(self.pts_count))
        
        return data.getvalue()

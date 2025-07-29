from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, Vector
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class UpdateDeleteChannelMessages(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.Update`.

    Details:
        - Layer: ``135``
        - ID: ``-0x3cd2a4ee``

    Parameters:
        channel_id: ``int`` ``64-bit``
        messages: List of ``int`` ``32-bit``
        pts: ``int`` ``32-bit``
        pts_count: ``int`` ``32-bit``
    """

    __slots__: List[str] = ["channel_id", "messages", "pts", "pts_count"]

    ID = -0x3cd2a4ee
    QUALNAME = "types.UpdateDeleteChannelMessages"

    def __init__(self, *, channel_id: int, messages: List[int], pts: int, pts_count: int) -> None:
        self.channel_id = channel_id  # long
        self.messages = messages  # Vector<int>
        self.pts = pts  # int
        self.pts_count = pts_count  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        channel_id = Long.read(data)
        
        messages = TLObject.read(data, Int)
        
        pts = Int.read(data)
        
        pts_count = Int.read(data)
        
        return UpdateDeleteChannelMessages(channel_id=channel_id, messages=messages, pts=pts, pts_count=pts_count)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Long(self.channel_id))
        
        data.write(Vector(self.messages, Int))
        
        data.write(Int(self.pts))
        
        data.write(Int(self.pts_count))
        
        return data.getvalue()

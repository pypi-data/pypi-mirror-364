from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, Vector
from pyeitaa.raw.core import TLObject
from typing import List, Optional, Any, Self


class UpdatePinnedChannelMessages(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.Update`.

    Details:
        - Layer: ``135``
        - ID: ``0x5bb98608``

    Parameters:
        channel_id: ``int`` ``64-bit``
        messages: List of ``int`` ``32-bit``
        pts: ``int`` ``32-bit``
        pts_count: ``int`` ``32-bit``
        pinned (optional): ``bool``
    """

    __slots__: List[str] = ["channel_id", "messages", "pts", "pts_count", "pinned"]

    ID = 0x5bb98608
    QUALNAME = "types.UpdatePinnedChannelMessages"

    def __init__(self, *, channel_id: int, messages: List[int], pts: int, pts_count: int, pinned: Optional[bool] = None) -> None:
        self.channel_id = channel_id  # long
        self.messages = messages  # Vector<int>
        self.pts = pts  # int
        self.pts_count = pts_count  # int
        self.pinned = pinned  # flags.0?true

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        pinned = True if flags & (1 << 0) else False
        channel_id = Long.read(data)
        
        messages = TLObject.read(data, Int)
        
        pts = Int.read(data)
        
        pts_count = Int.read(data)
        
        return UpdatePinnedChannelMessages(channel_id=channel_id, messages=messages, pts=pts, pts_count=pts_count, pinned=pinned)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.pinned else 0
        data.write(Int(flags))
        
        data.write(Long(self.channel_id))
        
        data.write(Vector(self.messages, Int))
        
        data.write(Int(self.pts))
        
        data.write(Int(self.pts_count))
        
        return data.getvalue()

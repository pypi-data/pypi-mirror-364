from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class UpdatePinnedMessages(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.Update`.

    Details:
        - Layer: ``135``
        - ID: ``-0x127a154b``

    Parameters:
        peer: :obj:`Peer <pyeitaa.raw.base.Peer>`
        messages: List of ``int`` ``32-bit``
        pts: ``int`` ``32-bit``
        pts_count: ``int`` ``32-bit``
        pinned (optional): ``bool``
    """

    __slots__: List[str] = ["peer", "messages", "pts", "pts_count", "pinned"]

    ID = -0x127a154b
    QUALNAME = "types.UpdatePinnedMessages"

    def __init__(self, *, peer: "raw.base.Peer", messages: List[int], pts: int, pts_count: int, pinned: Optional[bool] = None) -> None:
        self.peer = peer  # Peer
        self.messages = messages  # Vector<int>
        self.pts = pts  # int
        self.pts_count = pts_count  # int
        self.pinned = pinned  # flags.0?true

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        pinned = True if flags & (1 << 0) else False
        peer = TLObject.read(data)
        
        messages = TLObject.read(data, Int)
        
        pts = Int.read(data)
        
        pts_count = Int.read(data)
        
        return UpdatePinnedMessages(peer=peer, messages=messages, pts=pts, pts_count=pts_count, pinned=pinned)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.pinned else 0
        data.write(Int(flags))
        
        data.write(self.peer.write())
        
        data.write(Vector(self.messages, Int))
        
        data.write(Int(self.pts))
        
        data.write(Int(self.pts_count))
        
        return data.getvalue()

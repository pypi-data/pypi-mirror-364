from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class MessageReplies(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.MessageReplies`.

    Details:
        - Layer: ``135``
        - ID: ``-0x7c29f03e``

    Parameters:
        replies: ``int`` ``32-bit``
        replies_pts: ``int`` ``32-bit``
        comments (optional): ``bool``
        recent_repliers (optional): List of :obj:`Peer <pyeitaa.raw.base.Peer>`
        channel_id (optional): ``int`` ``64-bit``
        max_id (optional): ``int`` ``32-bit``
        read_max_id (optional): ``int`` ``32-bit``
    """

    __slots__: List[str] = ["replies", "replies_pts", "comments", "recent_repliers", "channel_id", "max_id", "read_max_id"]

    ID = -0x7c29f03e
    QUALNAME = "types.MessageReplies"

    def __init__(self, *, replies: int, replies_pts: int, comments: Optional[bool] = None, recent_repliers: Optional[List["raw.base.Peer"]] = None, channel_id: Optional[int] = None, max_id: Optional[int] = None, read_max_id: Optional[int] = None) -> None:
        self.replies = replies  # int
        self.replies_pts = replies_pts  # int
        self.comments = comments  # flags.0?true
        self.recent_repliers = recent_repliers  # flags.1?Vector<Peer>
        self.channel_id = channel_id  # flags.0?long
        self.max_id = max_id  # flags.2?int
        self.read_max_id = read_max_id  # flags.3?int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        comments = True if flags & (1 << 0) else False
        replies = Int.read(data)
        
        replies_pts = Int.read(data)
        
        recent_repliers = TLObject.read(data) if flags & (1 << 1) else []
        
        channel_id = Long.read(data) if flags & (1 << 0) else None
        max_id = Int.read(data) if flags & (1 << 2) else None
        read_max_id = Int.read(data) if flags & (1 << 3) else None
        return MessageReplies(replies=replies, replies_pts=replies_pts, comments=comments, recent_repliers=recent_repliers, channel_id=channel_id, max_id=max_id, read_max_id=read_max_id)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.comments else 0
        flags |= (1 << 1) if self.recent_repliers is not None else 0
        flags |= (1 << 0) if self.channel_id is not None else 0
        flags |= (1 << 2) if self.max_id is not None else 0
        flags |= (1 << 3) if self.read_max_id is not None else 0
        data.write(Int(flags))
        
        data.write(Int(self.replies))
        
        data.write(Int(self.replies_pts))
        
        if self.recent_repliers is not None:
            data.write(Vector(self.recent_repliers))
        
        if self.channel_id is not None:
            data.write(Long(self.channel_id))
        
        if self.max_id is not None:
            data.write(Int(self.max_id))
        
        if self.read_max_id is not None:
            data.write(Int(self.read_max_id))
        
        return data.getvalue()

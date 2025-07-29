from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long
from pyeitaa.raw.core import TLObject
from typing import List, Optional, Any, Self


class UpdateReadChannelDiscussionInbox(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.Update`.

    Details:
        - Layer: ``135``
        - ID: ``-0x294e6aba``

    Parameters:
        channel_id: ``int`` ``64-bit``
        top_msg_id: ``int`` ``32-bit``
        read_max_id: ``int`` ``32-bit``
        broadcast_id (optional): ``int`` ``64-bit``
        broadcast_post (optional): ``int`` ``32-bit``
    """

    __slots__: List[str] = ["channel_id", "top_msg_id", "read_max_id", "broadcast_id", "broadcast_post"]

    ID = -0x294e6aba
    QUALNAME = "types.UpdateReadChannelDiscussionInbox"

    def __init__(self, *, channel_id: int, top_msg_id: int, read_max_id: int, broadcast_id: Optional[int] = None, broadcast_post: Optional[int] = None) -> None:
        self.channel_id = channel_id  # long
        self.top_msg_id = top_msg_id  # int
        self.read_max_id = read_max_id  # int
        self.broadcast_id = broadcast_id  # flags.0?long
        self.broadcast_post = broadcast_post  # flags.0?int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        channel_id = Long.read(data)
        
        top_msg_id = Int.read(data)
        
        read_max_id = Int.read(data)
        
        broadcast_id = Long.read(data) if flags & (1 << 0) else None
        broadcast_post = Int.read(data) if flags & (1 << 0) else None
        return UpdateReadChannelDiscussionInbox(channel_id=channel_id, top_msg_id=top_msg_id, read_max_id=read_max_id, broadcast_id=broadcast_id, broadcast_post=broadcast_post)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.broadcast_id is not None else 0
        flags |= (1 << 0) if self.broadcast_post is not None else 0
        data.write(Int(flags))
        
        data.write(Long(self.channel_id))
        
        data.write(Int(self.top_msg_id))
        
        data.write(Int(self.read_max_id))
        
        if self.broadcast_id is not None:
            data.write(Long(self.broadcast_id))
        
        if self.broadcast_post is not None:
            data.write(Int(self.broadcast_post))
        
        return data.getvalue()

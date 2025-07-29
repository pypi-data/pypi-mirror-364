from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class MessageReplyHeader(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.MessageReplyHeader`.

    Details:
        - Layer: ``135``
        - ID: ``-0x592a889d``

    Parameters:
        reply_to_msg_id: ``int`` ``32-bit``
        reply_to_peer_id (optional): :obj:`Peer <pyeitaa.raw.base.Peer>`
        reply_to_top_id (optional): ``int`` ``32-bit``
    """

    __slots__: List[str] = ["reply_to_msg_id", "reply_to_peer_id", "reply_to_top_id"]

    ID = -0x592a889d
    QUALNAME = "types.MessageReplyHeader"

    def __init__(self, *, reply_to_msg_id: int, reply_to_peer_id: "raw.base.Peer" = None, reply_to_top_id: Optional[int] = None) -> None:
        self.reply_to_msg_id = reply_to_msg_id  # int
        self.reply_to_peer_id = reply_to_peer_id  # flags.0?Peer
        self.reply_to_top_id = reply_to_top_id  # flags.1?int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        reply_to_msg_id = Int.read(data)
        
        reply_to_peer_id = TLObject.read(data) if flags & (1 << 0) else None
        
        reply_to_top_id = Int.read(data) if flags & (1 << 1) else None
        return MessageReplyHeader(reply_to_msg_id=reply_to_msg_id, reply_to_peer_id=reply_to_peer_id, reply_to_top_id=reply_to_top_id)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.reply_to_peer_id is not None else 0
        flags |= (1 << 1) if self.reply_to_top_id is not None else 0
        data.write(Int(flags))
        
        data.write(Int(self.reply_to_msg_id))
        
        if self.reply_to_peer_id is not None:
            data.write(self.reply_to_peer_id.write())
        
        if self.reply_to_top_id is not None:
            data.write(Int(self.reply_to_top_id))
        
        return data.getvalue()

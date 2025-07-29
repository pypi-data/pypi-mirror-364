from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class MessageService(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.Message`.

    Details:
        - Layer: ``135``
        - ID: ``0x2b085862``

    Parameters:
        id: ``int`` ``32-bit``
        peer_id: :obj:`Peer <pyeitaa.raw.base.Peer>`
        date: ``int`` ``32-bit``
        action: :obj:`MessageAction <pyeitaa.raw.base.MessageAction>`
        out (optional): ``bool``
        mentioned (optional): ``bool``
        media_unread (optional): ``bool``
        silent (optional): ``bool``
        post (optional): ``bool``
        legacy (optional): ``bool``
        from_id (optional): :obj:`Peer <pyeitaa.raw.base.Peer>`
        reply_to (optional): :obj:`MessageReplyHeader <pyeitaa.raw.base.MessageReplyHeader>`
        ttl_period (optional): ``int`` ``32-bit``
    """

    __slots__: List[str] = ["id", "peer_id", "date", "action", "out", "mentioned", "media_unread", "silent", "post", "legacy", "from_id", "reply_to", "ttl_period"]

    ID = 0x2b085862
    QUALNAME = "types.MessageService"

    def __init__(self, *, id: int, peer_id: "raw.base.Peer", date: int, action: "raw.base.MessageAction", out: Optional[bool] = None, mentioned: Optional[bool] = None, media_unread: Optional[bool] = None, silent: Optional[bool] = None, post: Optional[bool] = None, legacy: Optional[bool] = None, from_id: "raw.base.Peer" = None, reply_to: "raw.base.MessageReplyHeader" = None, ttl_period: Optional[int] = None) -> None:
        self.id = id  # int
        self.peer_id = peer_id  # Peer
        self.date = date  # int
        self.action = action  # MessageAction
        self.out = out  # flags.1?true
        self.mentioned = mentioned  # flags.4?true
        self.media_unread = media_unread  # flags.5?true
        self.silent = silent  # flags.13?true
        self.post = post  # flags.14?true
        self.legacy = legacy  # flags.19?true
        self.from_id = from_id  # flags.8?Peer
        self.reply_to = reply_to  # flags.3?MessageReplyHeader
        self.ttl_period = ttl_period  # flags.25?int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        out = True if flags & (1 << 1) else False
        mentioned = True if flags & (1 << 4) else False
        media_unread = True if flags & (1 << 5) else False
        silent = True if flags & (1 << 13) else False
        post = True if flags & (1 << 14) else False
        legacy = True if flags & (1 << 19) else False
        id = Int.read(data)
        
        from_id = TLObject.read(data) if flags & (1 << 8) else None
        
        peer_id = TLObject.read(data)
        
        reply_to = TLObject.read(data) if flags & (1 << 3) else None
        
        date = Int.read(data)
        
        action = TLObject.read(data)
        
        ttl_period = Int.read(data) if flags & (1 << 25) else None
        return MessageService(id=id, peer_id=peer_id, date=date, action=action, out=out, mentioned=mentioned, media_unread=media_unread, silent=silent, post=post, legacy=legacy, from_id=from_id, reply_to=reply_to, ttl_period=ttl_period)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 1) if self.out else 0
        flags |= (1 << 4) if self.mentioned else 0
        flags |= (1 << 5) if self.media_unread else 0
        flags |= (1 << 13) if self.silent else 0
        flags |= (1 << 14) if self.post else 0
        flags |= (1 << 19) if self.legacy else 0
        flags |= (1 << 8) if self.from_id is not None else 0
        flags |= (1 << 3) if self.reply_to is not None else 0
        flags |= (1 << 25) if self.ttl_period is not None else 0
        data.write(Int(flags))
        
        data.write(Int(self.id))
        
        if self.from_id is not None:
            data.write(self.from_id.write())
        
        data.write(self.peer_id.write())
        
        if self.reply_to is not None:
            data.write(self.reply_to.write())
        
        data.write(Int(self.date))
        
        data.write(self.action.write())
        
        if self.ttl_period is not None:
            data.write(Int(self.ttl_period))
        
        return data.getvalue()

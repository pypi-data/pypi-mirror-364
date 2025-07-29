from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, String
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class SendInlineBotResult(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x220815b0``

    Parameters:
        peer: :obj:`InputPeer <pyeitaa.raw.base.InputPeer>`
        random_id: ``int`` ``64-bit``
        query_id: ``int`` ``64-bit``
        id: ``str``
        silent (optional): ``bool``
        background (optional): ``bool``
        clear_draft (optional): ``bool``
        hide_via (optional): ``bool``
        reply_to_msg_id (optional): ``int`` ``32-bit``
        schedule_date (optional): ``int`` ``32-bit``

    Returns:
        :obj:`Updates <pyeitaa.raw.base.Updates>`
    """

    __slots__: List[str] = ["peer", "random_id", "query_id", "id", "silent", "background", "clear_draft", "hide_via", "reply_to_msg_id", "schedule_date"]

    ID = 0x220815b0
    QUALNAME = "functions.messages.SendInlineBotResult"

    def __init__(self, *, peer: "raw.base.InputPeer", random_id: int, query_id: int, id: str, silent: Optional[bool] = None, background: Optional[bool] = None, clear_draft: Optional[bool] = None, hide_via: Optional[bool] = None, reply_to_msg_id: Optional[int] = None, schedule_date: Optional[int] = None) -> None:
        self.peer = peer  # InputPeer
        self.random_id = random_id  # long
        self.query_id = query_id  # long
        self.id = id  # string
        self.silent = silent  # flags.5?true
        self.background = background  # flags.6?true
        self.clear_draft = clear_draft  # flags.7?true
        self.hide_via = hide_via  # flags.11?true
        self.reply_to_msg_id = reply_to_msg_id  # flags.0?int
        self.schedule_date = schedule_date  # flags.10?int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        silent = True if flags & (1 << 5) else False
        background = True if flags & (1 << 6) else False
        clear_draft = True if flags & (1 << 7) else False
        hide_via = True if flags & (1 << 11) else False
        peer = TLObject.read(data)
        
        reply_to_msg_id = Int.read(data) if flags & (1 << 0) else None
        random_id = Long.read(data)
        
        query_id = Long.read(data)
        
        id = String.read(data)
        
        schedule_date = Int.read(data) if flags & (1 << 10) else None
        return SendInlineBotResult(peer=peer, random_id=random_id, query_id=query_id, id=id, silent=silent, background=background, clear_draft=clear_draft, hide_via=hide_via, reply_to_msg_id=reply_to_msg_id, schedule_date=schedule_date)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 5) if self.silent else 0
        flags |= (1 << 6) if self.background else 0
        flags |= (1 << 7) if self.clear_draft else 0
        flags |= (1 << 11) if self.hide_via else 0
        flags |= (1 << 0) if self.reply_to_msg_id is not None else 0
        flags |= (1 << 10) if self.schedule_date is not None else 0
        data.write(Int(flags))
        
        data.write(self.peer.write())
        
        if self.reply_to_msg_id is not None:
            data.write(Int(self.reply_to_msg_id))
        
        data.write(Long(self.random_id))
        
        data.write(Long(self.query_id))
        
        data.write(String(self.id))
        
        if self.schedule_date is not None:
            data.write(Int(self.schedule_date))
        
        return data.getvalue()

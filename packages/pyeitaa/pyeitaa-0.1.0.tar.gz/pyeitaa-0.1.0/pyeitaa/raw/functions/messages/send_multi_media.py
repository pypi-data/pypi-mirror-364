from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class SendMultiMedia(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x33feef35``

    Parameters:
        peer: :obj:`InputPeer <pyeitaa.raw.base.InputPeer>`
        multi_media: List of :obj:`InputSingleMedia <pyeitaa.raw.base.InputSingleMedia>`
        silent (optional): ``bool``
        background (optional): ``bool``
        clear_draft (optional): ``bool``
        reply_to_msg_id (optional): ``int`` ``32-bit``
        schedule_date (optional): ``int`` ``32-bit``
        noforwards (optional): ``bool``

    Returns:
        :obj:`Updates <pyeitaa.raw.base.Updates>`
    """

    __slots__: List[str] = ["peer", "multi_media", "silent", "background", "clear_draft", "reply_to_msg_id", "schedule_date", "noforwards"]

    ID = -0x33feef35
    QUALNAME = "functions.messages.SendMultiMedia"

    def __init__(self, *, peer: "raw.base.InputPeer", multi_media: List["raw.base.InputSingleMedia"], silent: Optional[bool] = None, background: Optional[bool] = None, clear_draft: Optional[bool] = None, reply_to_msg_id: Optional[int] = None, schedule_date: Optional[int] = None, noforwards: Optional[bool] = None) -> None:
        self.peer = peer  # InputPeer
        self.multi_media = multi_media  # Vector<InputSingleMedia>
        self.silent = silent  # flags.5?true
        self.background = background  # flags.6?true
        self.clear_draft = clear_draft  # flags.7?true
        self.reply_to_msg_id = reply_to_msg_id  # flags.0?int
        self.schedule_date = schedule_date  # flags.10?int
        self.noforwards = noforwards  # flags.14?true

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        silent = True if flags & (1 << 5) else False
        background = True if flags & (1 << 6) else False
        clear_draft = True if flags & (1 << 7) else False
        peer = TLObject.read(data)
        
        reply_to_msg_id = Int.read(data) if flags & (1 << 0) else None
        multi_media = TLObject.read(data)
        
        schedule_date = Int.read(data) if flags & (1 << 10) else None
        noforwards = True if flags & (1 << 14) else False
        return SendMultiMedia(peer=peer, multi_media=multi_media, silent=silent, background=background, clear_draft=clear_draft, reply_to_msg_id=reply_to_msg_id, schedule_date=schedule_date, noforwards=noforwards)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 5) if self.silent else 0
        flags |= (1 << 6) if self.background else 0
        flags |= (1 << 7) if self.clear_draft else 0
        flags |= (1 << 0) if self.reply_to_msg_id is not None else 0
        flags |= (1 << 10) if self.schedule_date is not None else 0
        flags |= (1 << 14) if self.noforwards else 0
        data.write(Int(flags))
        
        data.write(self.peer.write())
        
        if self.reply_to_msg_id is not None:
            data.write(Int(self.reply_to_msg_id))
        
        data.write(Vector(self.multi_media))
        
        if self.schedule_date is not None:
            data.write(Int(self.schedule_date))
        
        return data.getvalue()

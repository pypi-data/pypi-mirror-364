from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, String, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class SendMedia(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x3491eba9``

    Parameters:
        peer: :obj:`InputPeer <pyeitaa.raw.base.InputPeer>`
        media: :obj:`InputMedia <pyeitaa.raw.base.InputMedia>`
        message: ``str``
        random_id: ``int`` ``64-bit``
        silent (optional): ``bool``
        background (optional): ``bool``
        clear_draft (optional): ``bool``
        reply_to_msg_id (optional): ``int`` ``32-bit``
        reply_markup (optional): :obj:`ReplyMarkup <pyeitaa.raw.base.ReplyMarkup>`
        entities (optional): List of :obj:`MessageEntity <pyeitaa.raw.base.MessageEntity>`
        schedule_date (optional): ``int`` ``32-bit``
        noforwards (optional): ``bool``

    Returns:
        :obj:`Updates <pyeitaa.raw.base.Updates>`
    """

    __slots__: List[str] = ["peer", "media", "message", "random_id", "silent", "background", "clear_draft", "reply_to_msg_id", "reply_markup", "entities", "schedule_date", "noforwards"]

    ID = 0x3491eba9
    QUALNAME = "functions.messages.SendMedia"

    def __init__(self, *, peer: "raw.base.InputPeer", media: "raw.base.InputMedia", message: str, random_id: int, silent: Optional[bool] = None, background: Optional[bool] = None, clear_draft: Optional[bool] = None, reply_to_msg_id: Optional[int] = None, reply_markup: "raw.base.ReplyMarkup" = None, entities: Optional[List["raw.base.MessageEntity"]] = None, schedule_date: Optional[int] = None, noforwards: Optional[bool] = None) -> None:
        self.peer = peer  # InputPeer
        self.media = media  # InputMedia
        self.message = message  # string
        self.random_id = random_id  # long
        self.silent = silent  # flags.5?true
        self.background = background  # flags.6?true
        self.clear_draft = clear_draft  # flags.7?true
        self.reply_to_msg_id = reply_to_msg_id  # flags.0?int
        self.reply_markup = reply_markup  # flags.2?ReplyMarkup
        self.entities = entities  # flags.3?Vector<MessageEntity>
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
        media = TLObject.read(data)
        
        message = String.read(data)
        
        random_id = Long.read(data)
        
        reply_markup = TLObject.read(data) if flags & (1 << 2) else None
        
        entities = TLObject.read(data) if flags & (1 << 3) else []
        
        schedule_date = Int.read(data) if flags & (1 << 10) else None
        noforwards = True if flags & (1 << 14) else False
        return SendMedia(peer=peer, media=media, message=message, random_id=random_id, silent=silent, background=background, clear_draft=clear_draft, reply_to_msg_id=reply_to_msg_id, reply_markup=reply_markup, entities=entities, schedule_date=schedule_date, noforwards=noforwards)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 5) if self.silent else 0
        flags |= (1 << 6) if self.background else 0
        flags |= (1 << 7) if self.clear_draft else 0
        flags |= (1 << 0) if self.reply_to_msg_id is not None else 0
        flags |= (1 << 2) if self.reply_markup is not None else 0
        flags |= (1 << 3) if self.entities is not None else 0
        flags |= (1 << 10) if self.schedule_date is not None else 0
        flags |= (1 << 14) if self.noforwards else 0
        data.write(Int(flags))
        
        data.write(self.peer.write())
        
        if self.reply_to_msg_id is not None:
            data.write(Int(self.reply_to_msg_id))
        
        data.write(self.media.write())
        
        data.write(String(self.message))
        
        data.write(Long(self.random_id))
        
        if self.reply_markup is not None:
            data.write(self.reply_markup.write())
        
        if self.entities is not None:
            data.write(Vector(self.entities))
        
        if self.schedule_date is not None:
            data.write(Int(self.schedule_date))
        
        return data.getvalue()

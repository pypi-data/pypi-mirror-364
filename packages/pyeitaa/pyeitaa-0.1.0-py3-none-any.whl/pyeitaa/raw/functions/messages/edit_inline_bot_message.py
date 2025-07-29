from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class EditInlineBotMessage(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x7caa8246``

    Parameters:
        id: :obj:`InputBotInlineMessageID <pyeitaa.raw.base.InputBotInlineMessageID>`
        no_webpage (optional): ``bool``
        message (optional): ``str``
        media (optional): :obj:`InputMedia <pyeitaa.raw.base.InputMedia>`
        reply_markup (optional): :obj:`ReplyMarkup <pyeitaa.raw.base.ReplyMarkup>`
        entities (optional): List of :obj:`MessageEntity <pyeitaa.raw.base.MessageEntity>`

    Returns:
        ``bool``
    """

    __slots__: List[str] = ["id", "no_webpage", "message", "media", "reply_markup", "entities"]

    ID = -0x7caa8246
    QUALNAME = "functions.messages.EditInlineBotMessage"

    def __init__(self, *, id: "raw.base.InputBotInlineMessageID", no_webpage: Optional[bool] = None, message: Optional[str] = None, media: "raw.base.InputMedia" = None, reply_markup: "raw.base.ReplyMarkup" = None, entities: Optional[List["raw.base.MessageEntity"]] = None) -> None:
        self.id = id  # InputBotInlineMessageID
        self.no_webpage = no_webpage  # flags.1?true
        self.message = message  # flags.11?string
        self.media = media  # flags.14?InputMedia
        self.reply_markup = reply_markup  # flags.2?ReplyMarkup
        self.entities = entities  # flags.3?Vector<MessageEntity>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        no_webpage = True if flags & (1 << 1) else False
        id = TLObject.read(data)
        
        message = String.read(data) if flags & (1 << 11) else None
        media = TLObject.read(data) if flags & (1 << 14) else None
        
        reply_markup = TLObject.read(data) if flags & (1 << 2) else None
        
        entities = TLObject.read(data) if flags & (1 << 3) else []
        
        return EditInlineBotMessage(id=id, no_webpage=no_webpage, message=message, media=media, reply_markup=reply_markup, entities=entities)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 1) if self.no_webpage else 0
        flags |= (1 << 11) if self.message is not None else 0
        flags |= (1 << 14) if self.media is not None else 0
        flags |= (1 << 2) if self.reply_markup is not None else 0
        flags |= (1 << 3) if self.entities is not None else 0
        data.write(Int(flags))
        
        data.write(self.id.write())
        
        if self.message is not None:
            data.write(String(self.message))
        
        if self.media is not None:
            data.write(self.media.write())
        
        if self.reply_markup is not None:
            data.write(self.reply_markup.write())
        
        if self.entities is not None:
            data.write(Vector(self.entities))
        
        return data.getvalue()

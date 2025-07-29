from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class InputBotInlineMessageText(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.InputBotInlineMessage`.

    Details:
        - Layer: ``135``
        - ID: ``0x3dcd7a87``

    Parameters:
        message: ``str``
        no_webpage (optional): ``bool``
        entities (optional): List of :obj:`MessageEntity <pyeitaa.raw.base.MessageEntity>`
        reply_markup (optional): :obj:`ReplyMarkup <pyeitaa.raw.base.ReplyMarkup>`
    """

    __slots__: List[str] = ["message", "no_webpage", "entities", "reply_markup"]

    ID = 0x3dcd7a87
    QUALNAME = "types.InputBotInlineMessageText"

    def __init__(self, *, message: str, no_webpage: Optional[bool] = None, entities: Optional[List["raw.base.MessageEntity"]] = None, reply_markup: "raw.base.ReplyMarkup" = None) -> None:
        self.message = message  # string
        self.no_webpage = no_webpage  # flags.0?true
        self.entities = entities  # flags.1?Vector<MessageEntity>
        self.reply_markup = reply_markup  # flags.2?ReplyMarkup

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        no_webpage = True if flags & (1 << 0) else False
        message = String.read(data)
        
        entities = TLObject.read(data) if flags & (1 << 1) else []
        
        reply_markup = TLObject.read(data) if flags & (1 << 2) else None
        
        return InputBotInlineMessageText(message=message, no_webpage=no_webpage, entities=entities, reply_markup=reply_markup)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.no_webpage else 0
        flags |= (1 << 1) if self.entities is not None else 0
        flags |= (1 << 2) if self.reply_markup is not None else 0
        data.write(Int(flags))
        
        data.write(String(self.message))
        
        if self.entities is not None:
            data.write(Vector(self.entities))
        
        if self.reply_markup is not None:
            data.write(self.reply_markup.write())
        
        return data.getvalue()

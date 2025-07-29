from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class BotInlineMessageMediaContact(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.BotInlineMessage`.

    Details:
        - Layer: ``135``
        - ID: ``0x18d1cdc2``

    Parameters:
        phone_number: ``str``
        first_name: ``str``
        last_name: ``str``
        vcard: ``str``
        reply_markup (optional): :obj:`ReplyMarkup <pyeitaa.raw.base.ReplyMarkup>`
    """

    __slots__: List[str] = ["phone_number", "first_name", "last_name", "vcard", "reply_markup"]

    ID = 0x18d1cdc2
    QUALNAME = "types.BotInlineMessageMediaContact"

    def __init__(self, *, phone_number: str, first_name: str, last_name: str, vcard: str, reply_markup: "raw.base.ReplyMarkup" = None) -> None:
        self.phone_number = phone_number  # string
        self.first_name = first_name  # string
        self.last_name = last_name  # string
        self.vcard = vcard  # string
        self.reply_markup = reply_markup  # flags.2?ReplyMarkup

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        phone_number = String.read(data)
        
        first_name = String.read(data)
        
        last_name = String.read(data)
        
        vcard = String.read(data)
        
        reply_markup = TLObject.read(data) if flags & (1 << 2) else None
        
        return BotInlineMessageMediaContact(phone_number=phone_number, first_name=first_name, last_name=last_name, vcard=vcard, reply_markup=reply_markup)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 2) if self.reply_markup is not None else 0
        data.write(Int(flags))
        
        data.write(String(self.phone_number))
        
        data.write(String(self.first_name))
        
        data.write(String(self.last_name))
        
        data.write(String(self.vcard))
        
        if self.reply_markup is not None:
            data.write(self.reply_markup.write())
        
        return data.getvalue()

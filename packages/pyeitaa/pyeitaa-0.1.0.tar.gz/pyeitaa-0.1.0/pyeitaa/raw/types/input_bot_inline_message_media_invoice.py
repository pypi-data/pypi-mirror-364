from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Bytes, String
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class InputBotInlineMessageMediaInvoice(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.InputBotInlineMessage`.

    Details:
        - Layer: ``135``
        - ID: ``-0x28187ddb``

    Parameters:
        title: ``str``
        description: ``str``
        invoice: :obj:`Invoice <pyeitaa.raw.base.Invoice>`
        payload: ``bytes``
        provider: ``str``
        provider_data: :obj:`DataJSON <pyeitaa.raw.base.DataJSON>`
        photo (optional): :obj:`InputWebDocument <pyeitaa.raw.base.InputWebDocument>`
        reply_markup (optional): :obj:`ReplyMarkup <pyeitaa.raw.base.ReplyMarkup>`
    """

    __slots__: List[str] = ["title", "description", "invoice", "payload", "provider", "provider_data", "photo", "reply_markup"]

    ID = -0x28187ddb
    QUALNAME = "types.InputBotInlineMessageMediaInvoice"

    def __init__(self, *, title: str, description: str, invoice: "raw.base.Invoice", payload: bytes, provider: str, provider_data: "raw.base.DataJSON", photo: "raw.base.InputWebDocument" = None, reply_markup: "raw.base.ReplyMarkup" = None) -> None:
        self.title = title  # string
        self.description = description  # string
        self.invoice = invoice  # Invoice
        self.payload = payload  # bytes
        self.provider = provider  # string
        self.provider_data = provider_data  # DataJSON
        self.photo = photo  # flags.0?InputWebDocument
        self.reply_markup = reply_markup  # flags.2?ReplyMarkup

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        title = String.read(data)
        
        description = String.read(data)
        
        photo = TLObject.read(data) if flags & (1 << 0) else None
        
        invoice = TLObject.read(data)
        
        payload = Bytes.read(data)
        
        provider = String.read(data)
        
        provider_data = TLObject.read(data)
        
        reply_markup = TLObject.read(data) if flags & (1 << 2) else None
        
        return InputBotInlineMessageMediaInvoice(title=title, description=description, invoice=invoice, payload=payload, provider=provider, provider_data=provider_data, photo=photo, reply_markup=reply_markup)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.photo is not None else 0
        flags |= (1 << 2) if self.reply_markup is not None else 0
        data.write(Int(flags))
        
        data.write(String(self.title))
        
        data.write(String(self.description))
        
        if self.photo is not None:
            data.write(self.photo.write())
        
        data.write(self.invoice.write())
        
        data.write(Bytes(self.payload))
        
        data.write(String(self.provider))
        
        data.write(self.provider_data.write())
        
        if self.reply_markup is not None:
            data.write(self.reply_markup.write())
        
        return data.getvalue()

from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Bytes, String
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class InputMediaInvoice(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.InputMedia`.

    Details:
        - Layer: ``135``
        - ID: ``-0x2686678c``

    Parameters:
        title: ``str``
        description: ``str``
        invoice: :obj:`Invoice <pyeitaa.raw.base.Invoice>`
        payload: ``bytes``
        provider: ``str``
        provider_data: :obj:`DataJSON <pyeitaa.raw.base.DataJSON>`
        photo (optional): :obj:`InputWebDocument <pyeitaa.raw.base.InputWebDocument>`
        start_param (optional): ``str``
    """

    __slots__: List[str] = ["title", "description", "invoice", "payload", "provider", "provider_data", "photo", "start_param"]

    ID = -0x2686678c
    QUALNAME = "types.InputMediaInvoice"

    def __init__(self, *, title: str, description: str, invoice: "raw.base.Invoice", payload: bytes, provider: str, provider_data: "raw.base.DataJSON", photo: "raw.base.InputWebDocument" = None, start_param: Optional[str] = None) -> None:
        self.title = title  # string
        self.description = description  # string
        self.invoice = invoice  # Invoice
        self.payload = payload  # bytes
        self.provider = provider  # string
        self.provider_data = provider_data  # DataJSON
        self.photo = photo  # flags.0?InputWebDocument
        self.start_param = start_param  # flags.1?string

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
        
        start_param = String.read(data) if flags & (1 << 1) else None
        return InputMediaInvoice(title=title, description=description, invoice=invoice, payload=payload, provider=provider, provider_data=provider_data, photo=photo, start_param=start_param)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.photo is not None else 0
        flags |= (1 << 1) if self.start_param is not None else 0
        data.write(Int(flags))
        
        data.write(String(self.title))
        
        data.write(String(self.description))
        
        if self.photo is not None:
            data.write(self.photo.write())
        
        data.write(self.invoice.write())
        
        data.write(Bytes(self.payload))
        
        data.write(String(self.provider))
        
        data.write(self.provider_data.write())
        
        if self.start_param is not None:
            data.write(String(self.start_param))
        
        return data.getvalue()

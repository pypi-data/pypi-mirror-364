from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, String
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class MessageMediaInvoice(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.MessageMedia`.

    Details:
        - Layer: ``135``
        - ID: ``-0x7baaecb9``

    Parameters:
        title: ``str``
        description: ``str``
        currency: ``str``
        total_amount: ``int`` ``64-bit``
        start_param: ``str``
        shipping_address_requested (optional): ``bool``
        test (optional): ``bool``
        photo (optional): :obj:`WebDocument <pyeitaa.raw.base.WebDocument>`
        receipt_msg_id (optional): ``int`` ``32-bit``

    See Also:
        This object can be returned by 3 methods:

        .. hlist::
            :columns: 2

            - :obj:`messages.GetWebPagePreview <pyeitaa.raw.functions.messages.GetWebPagePreview>`
            - :obj:`messages.UploadMedia <pyeitaa.raw.functions.messages.UploadMedia>`
            - :obj:`messages.UploadImportedMedia <pyeitaa.raw.functions.messages.UploadImportedMedia>`
    """

    __slots__: List[str] = ["title", "description", "currency", "total_amount", "start_param", "shipping_address_requested", "test", "photo", "receipt_msg_id"]

    ID = -0x7baaecb9
    QUALNAME = "types.MessageMediaInvoice"

    def __init__(self, *, title: str, description: str, currency: str, total_amount: int, start_param: str, shipping_address_requested: Optional[bool] = None, test: Optional[bool] = None, photo: "raw.base.WebDocument" = None, receipt_msg_id: Optional[int] = None) -> None:
        self.title = title  # string
        self.description = description  # string
        self.currency = currency  # string
        self.total_amount = total_amount  # long
        self.start_param = start_param  # string
        self.shipping_address_requested = shipping_address_requested  # flags.1?true
        self.test = test  # flags.3?true
        self.photo = photo  # flags.0?WebDocument
        self.receipt_msg_id = receipt_msg_id  # flags.2?int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        shipping_address_requested = True if flags & (1 << 1) else False
        test = True if flags & (1 << 3) else False
        title = String.read(data)
        
        description = String.read(data)
        
        photo = TLObject.read(data) if flags & (1 << 0) else None
        
        receipt_msg_id = Int.read(data) if flags & (1 << 2) else None
        currency = String.read(data)
        
        total_amount = Long.read(data)
        
        start_param = String.read(data)
        
        return MessageMediaInvoice(title=title, description=description, currency=currency, total_amount=total_amount, start_param=start_param, shipping_address_requested=shipping_address_requested, test=test, photo=photo, receipt_msg_id=receipt_msg_id)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 1) if self.shipping_address_requested else 0
        flags |= (1 << 3) if self.test else 0
        flags |= (1 << 0) if self.photo is not None else 0
        flags |= (1 << 2) if self.receipt_msg_id is not None else 0
        data.write(Int(flags))
        
        data.write(String(self.title))
        
        data.write(String(self.description))
        
        if self.photo is not None:
            data.write(self.photo.write())
        
        if self.receipt_msg_id is not None:
            data.write(Int(self.receipt_msg_id))
        
        data.write(String(self.currency))
        
        data.write(Long(self.total_amount))
        
        data.write(String(self.start_param))
        
        return data.getvalue()

from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class PaymentRequestedInfo(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.PaymentRequestedInfo`.

    Details:
        - Layer: ``135``
        - ID: ``-0x6f63c06c``

    Parameters:
        name (optional): ``str``
        phone (optional): ``str``
        email (optional): ``str``
        shipping_address (optional): :obj:`PostAddress <pyeitaa.raw.base.PostAddress>`
    """

    __slots__: List[str] = ["name", "phone", "email", "shipping_address"]

    ID = -0x6f63c06c
    QUALNAME = "types.PaymentRequestedInfo"

    def __init__(self, *, name: Optional[str] = None, phone: Optional[str] = None, email: Optional[str] = None, shipping_address: "raw.base.PostAddress" = None) -> None:
        self.name = name  # flags.0?string
        self.phone = phone  # flags.1?string
        self.email = email  # flags.2?string
        self.shipping_address = shipping_address  # flags.3?PostAddress

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        name = String.read(data) if flags & (1 << 0) else None
        phone = String.read(data) if flags & (1 << 1) else None
        email = String.read(data) if flags & (1 << 2) else None
        shipping_address = TLObject.read(data) if flags & (1 << 3) else None
        
        return PaymentRequestedInfo(name=name, phone=phone, email=email, shipping_address=shipping_address)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.name is not None else 0
        flags |= (1 << 1) if self.phone is not None else 0
        flags |= (1 << 2) if self.email is not None else 0
        flags |= (1 << 3) if self.shipping_address is not None else 0
        data.write(Int(flags))
        
        if self.name is not None:
            data.write(String(self.name))
        
        if self.phone is not None:
            data.write(String(self.phone))
        
        if self.email is not None:
            data.write(String(self.email))
        
        if self.shipping_address is not None:
            data.write(self.shipping_address.write())
        
        return data.getvalue()

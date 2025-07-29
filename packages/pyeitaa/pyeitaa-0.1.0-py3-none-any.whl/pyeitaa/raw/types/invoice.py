from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, String, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class Invoice(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.Invoice`.

    Details:
        - Layer: ``135``
        - ID: ``0xcd886e0``

    Parameters:
        currency: ``str``
        prices: List of :obj:`LabeledPrice <pyeitaa.raw.base.LabeledPrice>`
        test (optional): ``bool``
        name_requested (optional): ``bool``
        phone_requested (optional): ``bool``
        email_requested (optional): ``bool``
        shipping_address_requested (optional): ``bool``
        flexible (optional): ``bool``
        phone_to_provider (optional): ``bool``
        email_to_provider (optional): ``bool``
        max_tip_amount (optional): ``int`` ``64-bit``
        suggested_tip_amounts (optional): List of ``int`` ``64-bit``
    """

    __slots__: List[str] = ["currency", "prices", "test", "name_requested", "phone_requested", "email_requested", "shipping_address_requested", "flexible", "phone_to_provider", "email_to_provider", "max_tip_amount", "suggested_tip_amounts"]

    ID = 0xcd886e0
    QUALNAME = "types.Invoice"

    def __init__(self, *, currency: str, prices: List["raw.base.LabeledPrice"], test: Optional[bool] = None, name_requested: Optional[bool] = None, phone_requested: Optional[bool] = None, email_requested: Optional[bool] = None, shipping_address_requested: Optional[bool] = None, flexible: Optional[bool] = None, phone_to_provider: Optional[bool] = None, email_to_provider: Optional[bool] = None, max_tip_amount: Optional[int] = None, suggested_tip_amounts: Optional[List[int]] = None) -> None:
        self.currency = currency  # string
        self.prices = prices  # Vector<LabeledPrice>
        self.test = test  # flags.0?true
        self.name_requested = name_requested  # flags.1?true
        self.phone_requested = phone_requested  # flags.2?true
        self.email_requested = email_requested  # flags.3?true
        self.shipping_address_requested = shipping_address_requested  # flags.4?true
        self.flexible = flexible  # flags.5?true
        self.phone_to_provider = phone_to_provider  # flags.6?true
        self.email_to_provider = email_to_provider  # flags.7?true
        self.max_tip_amount = max_tip_amount  # flags.8?long
        self.suggested_tip_amounts = suggested_tip_amounts  # flags.8?Vector<long>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        test = True if flags & (1 << 0) else False
        name_requested = True if flags & (1 << 1) else False
        phone_requested = True if flags & (1 << 2) else False
        email_requested = True if flags & (1 << 3) else False
        shipping_address_requested = True if flags & (1 << 4) else False
        flexible = True if flags & (1 << 5) else False
        phone_to_provider = True if flags & (1 << 6) else False
        email_to_provider = True if flags & (1 << 7) else False
        currency = String.read(data)
        
        prices = TLObject.read(data)
        
        max_tip_amount = Long.read(data) if flags & (1 << 8) else None
        suggested_tip_amounts = TLObject.read(data, Long) if flags & (1 << 8) else []
        
        return Invoice(currency=currency, prices=prices, test=test, name_requested=name_requested, phone_requested=phone_requested, email_requested=email_requested, shipping_address_requested=shipping_address_requested, flexible=flexible, phone_to_provider=phone_to_provider, email_to_provider=email_to_provider, max_tip_amount=max_tip_amount, suggested_tip_amounts=suggested_tip_amounts)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.test else 0
        flags |= (1 << 1) if self.name_requested else 0
        flags |= (1 << 2) if self.phone_requested else 0
        flags |= (1 << 3) if self.email_requested else 0
        flags |= (1 << 4) if self.shipping_address_requested else 0
        flags |= (1 << 5) if self.flexible else 0
        flags |= (1 << 6) if self.phone_to_provider else 0
        flags |= (1 << 7) if self.email_to_provider else 0
        flags |= (1 << 8) if self.max_tip_amount is not None else 0
        flags |= (1 << 8) if self.suggested_tip_amounts is not None else 0
        data.write(Int(flags))
        
        data.write(String(self.currency))
        
        data.write(Vector(self.prices))
        
        if self.max_tip_amount is not None:
            data.write(Long(self.max_tip_amount))
        
        if self.suggested_tip_amounts is not None:
            data.write(Vector(self.suggested_tip_amounts, Long))
        
        return data.getvalue()

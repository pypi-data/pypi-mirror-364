from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, Bytes, String
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class MessageActionPaymentSentMe(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.MessageAction`.

    Details:
        - Layer: ``135``
        - ID: ``-0x70ce4cd9``

    Parameters:
        currency: ``str``
        total_amount: ``int`` ``64-bit``
        payload: ``bytes``
        charge: :obj:`PaymentCharge <pyeitaa.raw.base.PaymentCharge>`
        info (optional): :obj:`PaymentRequestedInfo <pyeitaa.raw.base.PaymentRequestedInfo>`
        shipping_option_id (optional): ``str``
    """

    __slots__: List[str] = ["currency", "total_amount", "payload", "charge", "info", "shipping_option_id"]

    ID = -0x70ce4cd9
    QUALNAME = "types.MessageActionPaymentSentMe"

    def __init__(self, *, currency: str, total_amount: int, payload: bytes, charge: "raw.base.PaymentCharge", info: "raw.base.PaymentRequestedInfo" = None, shipping_option_id: Optional[str] = None) -> None:
        self.currency = currency  # string
        self.total_amount = total_amount  # long
        self.payload = payload  # bytes
        self.charge = charge  # PaymentCharge
        self.info = info  # flags.0?PaymentRequestedInfo
        self.shipping_option_id = shipping_option_id  # flags.1?string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        currency = String.read(data)
        
        total_amount = Long.read(data)
        
        payload = Bytes.read(data)
        
        info = TLObject.read(data) if flags & (1 << 0) else None
        
        shipping_option_id = String.read(data) if flags & (1 << 1) else None
        charge = TLObject.read(data)
        
        return MessageActionPaymentSentMe(currency=currency, total_amount=total_amount, payload=payload, charge=charge, info=info, shipping_option_id=shipping_option_id)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.info is not None else 0
        flags |= (1 << 1) if self.shipping_option_id is not None else 0
        data.write(Int(flags))
        
        data.write(String(self.currency))
        
        data.write(Long(self.total_amount))
        
        data.write(Bytes(self.payload))
        
        if self.info is not None:
            data.write(self.info.write())
        
        if self.shipping_option_id is not None:
            data.write(String(self.shipping_option_id))
        
        data.write(self.charge.write())
        
        return data.getvalue()

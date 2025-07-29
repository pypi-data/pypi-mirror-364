from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, Bytes, String
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class UpdateBotPrecheckoutQuery(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.Update`.

    Details:
        - Layer: ``135``
        - ID: ``-0x7355656a``

    Parameters:
        query_id: ``int`` ``64-bit``
        user_id: ``int`` ``64-bit``
        payload: ``bytes``
        currency: ``str``
        total_amount: ``int`` ``64-bit``
        info (optional): :obj:`PaymentRequestedInfo <pyeitaa.raw.base.PaymentRequestedInfo>`
        shipping_option_id (optional): ``str``
    """

    __slots__: List[str] = ["query_id", "user_id", "payload", "currency", "total_amount", "info", "shipping_option_id"]

    ID = -0x7355656a
    QUALNAME = "types.UpdateBotPrecheckoutQuery"

    def __init__(self, *, query_id: int, user_id: int, payload: bytes, currency: str, total_amount: int, info: "raw.base.PaymentRequestedInfo" = None, shipping_option_id: Optional[str] = None) -> None:
        self.query_id = query_id  # long
        self.user_id = user_id  # long
        self.payload = payload  # bytes
        self.currency = currency  # string
        self.total_amount = total_amount  # long
        self.info = info  # flags.0?PaymentRequestedInfo
        self.shipping_option_id = shipping_option_id  # flags.1?string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        query_id = Long.read(data)
        
        user_id = Long.read(data)
        
        payload = Bytes.read(data)
        
        info = TLObject.read(data) if flags & (1 << 0) else None
        
        shipping_option_id = String.read(data) if flags & (1 << 1) else None
        currency = String.read(data)
        
        total_amount = Long.read(data)
        
        return UpdateBotPrecheckoutQuery(query_id=query_id, user_id=user_id, payload=payload, currency=currency, total_amount=total_amount, info=info, shipping_option_id=shipping_option_id)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.info is not None else 0
        flags |= (1 << 1) if self.shipping_option_id is not None else 0
        data.write(Int(flags))
        
        data.write(Long(self.query_id))
        
        data.write(Long(self.user_id))
        
        data.write(Bytes(self.payload))
        
        if self.info is not None:
            data.write(self.info.write())
        
        if self.shipping_option_id is not None:
            data.write(String(self.shipping_option_id))
        
        data.write(String(self.currency))
        
        data.write(Long(self.total_amount))
        
        return data.getvalue()

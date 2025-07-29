from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, String
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class MessageActionPaymentSent(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.MessageAction`.

    Details:
        - Layer: ``135``
        - ID: ``0x40699cd0``

    Parameters:
        currency: ``str``
        total_amount: ``int`` ``64-bit``
    """

    __slots__: List[str] = ["currency", "total_amount"]

    ID = 0x40699cd0
    QUALNAME = "types.MessageActionPaymentSent"

    def __init__(self, *, currency: str, total_amount: int) -> None:
        self.currency = currency  # string
        self.total_amount = total_amount  # long

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        currency = String.read(data)
        
        total_amount = Long.read(data)
        
        return MessageActionPaymentSent(currency=currency, total_amount=total_amount)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(String(self.currency))
        
        data.write(Long(self.total_amount))
        
        return data.getvalue()

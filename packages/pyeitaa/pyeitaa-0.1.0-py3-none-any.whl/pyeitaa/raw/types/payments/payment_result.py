from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class PaymentResult(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.payments.PaymentResult`.

    Details:
        - Layer: ``135``
        - ID: ``0x4e5f810d``

    Parameters:
        updates: :obj:`Updates <pyeitaa.raw.base.Updates>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`payments.SendPaymentForm <pyeitaa.raw.functions.payments.SendPaymentForm>`
    """

    __slots__: List[str] = ["updates"]

    ID = 0x4e5f810d
    QUALNAME = "types.payments.PaymentResult"

    def __init__(self, *, updates: "raw.base.Updates") -> None:
        self.updates = updates  # Updates

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        updates = TLObject.read(data)
        
        return PaymentResult(updates=updates)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.updates.write())
        
        return data.getvalue()

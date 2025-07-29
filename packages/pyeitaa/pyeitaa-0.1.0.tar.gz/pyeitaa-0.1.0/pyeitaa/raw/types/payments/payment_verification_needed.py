from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class PaymentVerificationNeeded(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.payments.PaymentResult`.

    Details:
        - Layer: ``135``
        - ID: ``-0x27beeec7``

    Parameters:
        url: ``str``

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`payments.SendPaymentForm <pyeitaa.raw.functions.payments.SendPaymentForm>`
    """

    __slots__: List[str] = ["url"]

    ID = -0x27beeec7
    QUALNAME = "types.payments.PaymentVerificationNeeded"

    def __init__(self, *, url: str) -> None:
        self.url = url  # string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        url = String.read(data)
        
        return PaymentVerificationNeeded(url=url)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(String(self.url))
        
        return data.getvalue()

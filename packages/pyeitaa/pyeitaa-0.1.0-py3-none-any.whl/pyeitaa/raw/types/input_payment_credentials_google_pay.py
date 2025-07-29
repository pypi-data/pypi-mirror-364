from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class InputPaymentCredentialsGooglePay(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.InputPaymentCredentials`.

    Details:
        - Layer: ``135``
        - ID: ``-0x753cd7ff``

    Parameters:
        payment_token: :obj:`DataJSON <pyeitaa.raw.base.DataJSON>`
    """

    __slots__: List[str] = ["payment_token"]

    ID = -0x753cd7ff
    QUALNAME = "types.InputPaymentCredentialsGooglePay"

    def __init__(self, *, payment_token: "raw.base.DataJSON") -> None:
        self.payment_token = payment_token  # DataJSON

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        payment_token = TLObject.read(data)
        
        return InputPaymentCredentialsGooglePay(payment_token=payment_token)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.payment_token.write())
        
        return data.getvalue()

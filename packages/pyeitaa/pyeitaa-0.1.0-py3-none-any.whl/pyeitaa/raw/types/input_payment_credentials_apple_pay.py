from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class InputPaymentCredentialsApplePay(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.InputPaymentCredentials`.

    Details:
        - Layer: ``135``
        - ID: ``0xaa1c39f``

    Parameters:
        payment_data: :obj:`DataJSON <pyeitaa.raw.base.DataJSON>`
    """

    __slots__: List[str] = ["payment_data"]

    ID = 0xaa1c39f
    QUALNAME = "types.InputPaymentCredentialsApplePay"

    def __init__(self, *, payment_data: "raw.base.DataJSON") -> None:
        self.payment_data = payment_data  # DataJSON

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        payment_data = TLObject.read(data)
        
        return InputPaymentCredentialsApplePay(payment_data=payment_data)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.payment_data.write())
        
        return data.getvalue()

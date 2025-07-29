from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class GetBankCardData(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x2e79d779``

    Parameters:
        number: ``str``

    Returns:
        :obj:`payments.BankCardData <pyeitaa.raw.base.payments.BankCardData>`
    """

    __slots__: List[str] = ["number"]

    ID = 0x2e79d779
    QUALNAME = "functions.payments.GetBankCardData"

    def __init__(self, *, number: str) -> None:
        self.number = number  # string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        number = String.read(data)
        
        return GetBankCardData(number=number)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(String(self.number))
        
        return data.getvalue()

from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class PaymentSavedCredentialsCard(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.PaymentSavedCredentials`.

    Details:
        - Layer: ``135``
        - ID: ``-0x323d85e1``

    Parameters:
        id: ``str``
        title: ``str``
    """

    __slots__: List[str] = ["id", "title"]

    ID = -0x323d85e1
    QUALNAME = "types.PaymentSavedCredentialsCard"

    def __init__(self, *, id: str, title: str) -> None:
        self.id = id  # string
        self.title = title  # string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        id = String.read(data)
        
        title = String.read(data)
        
        return PaymentSavedCredentialsCard(id=id, title=title)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(String(self.id))
        
        data.write(String(self.title))
        
        return data.getvalue()

from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class CancelCode(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x1f040578``

    Parameters:
        phone_number: ``str``
        phone_code_hash: ``str``

    Returns:
        ``bool``
    """

    __slots__: List[str] = ["phone_number", "phone_code_hash"]

    ID = 0x1f040578
    QUALNAME = "functions.auth.CancelCode"

    def __init__(self, *, phone_number: str, phone_code_hash: str) -> None:
        self.phone_number = phone_number  # string
        self.phone_code_hash = phone_code_hash  # string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        phone_number = String.read(data)
        
        phone_code_hash = String.read(data)
        
        return CancelCode(phone_number=phone_number, phone_code_hash=phone_code_hash)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(String(self.phone_number))
        
        data.write(String(self.phone_code_hash))
        
        return data.getvalue()

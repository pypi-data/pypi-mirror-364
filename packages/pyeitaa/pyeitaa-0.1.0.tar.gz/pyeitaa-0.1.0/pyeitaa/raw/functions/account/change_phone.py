from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class ChangePhone(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x70c32edb``

    Parameters:
        phone_number: ``str``
        phone_code_hash: ``str``
        phone_code: ``str``

    Returns:
        :obj:`User <pyeitaa.raw.base.User>`
    """

    __slots__: List[str] = ["phone_number", "phone_code_hash", "phone_code"]

    ID = 0x70c32edb
    QUALNAME = "functions.account.ChangePhone"

    def __init__(self, *, phone_number: str, phone_code_hash: str, phone_code: str) -> None:
        self.phone_number = phone_number  # string
        self.phone_code_hash = phone_code_hash  # string
        self.phone_code = phone_code  # string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        phone_number = String.read(data)
        
        phone_code_hash = String.read(data)
        
        phone_code = String.read(data)
        
        return ChangePhone(phone_number=phone_number, phone_code_hash=phone_code_hash, phone_code=phone_code)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(String(self.phone_number))
        
        data.write(String(self.phone_code_hash))
        
        data.write(String(self.phone_code))
        
        return data.getvalue()

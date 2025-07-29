from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class VerifyTwoStepVerificationCode(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x57adaa15``

    Parameters:
        phone_code_hash: ``str``
        phone_code: ``str``

    Returns:
        ``bool``
    """

    __slots__: List[str] = ["phone_code_hash", "phone_code"]

    ID = 0x57adaa15
    QUALNAME = "functions.VerifyTwoStepVerificationCode"

    def __init__(self, *, phone_code_hash: str, phone_code: str) -> None:
        self.phone_code_hash = phone_code_hash  # string
        self.phone_code = phone_code  # string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        phone_code_hash = String.read(data)
        
        phone_code = String.read(data)
        
        return VerifyTwoStepVerificationCode(phone_code_hash=phone_code_hash, phone_code=phone_code)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(String(self.phone_code_hash))
        
        data.write(String(self.phone_code))
        
        return data.getvalue()

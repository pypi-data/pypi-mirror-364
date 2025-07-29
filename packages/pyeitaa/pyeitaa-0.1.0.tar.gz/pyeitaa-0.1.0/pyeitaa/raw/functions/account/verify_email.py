from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class VerifyEmail(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x1345c625``

    Parameters:
        email: ``str``
        code: ``str``

    Returns:
        ``bool``
    """

    __slots__: List[str] = ["email", "code"]

    ID = -0x1345c625
    QUALNAME = "functions.account.VerifyEmail"

    def __init__(self, *, email: str, code: str) -> None:
        self.email = email  # string
        self.code = code  # string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        email = String.read(data)
        
        code = String.read(data)
        
        return VerifyEmail(email=email, code=code)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(String(self.email))
        
        data.write(String(self.code))
        
        return data.getvalue()

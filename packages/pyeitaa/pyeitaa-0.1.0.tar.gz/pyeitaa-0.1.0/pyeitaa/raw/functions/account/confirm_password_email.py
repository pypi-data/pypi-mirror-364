from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class ConfirmPasswordEmail(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x7020e6e0``

    Parameters:
        code: ``str``

    Returns:
        ``bool``
    """

    __slots__: List[str] = ["code"]

    ID = -0x7020e6e0
    QUALNAME = "functions.account.ConfirmPasswordEmail"

    def __init__(self, *, code: str) -> None:
        self.code = code  # string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        code = String.read(data)
        
        return ConfirmPasswordEmail(code=code)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(String(self.code))
        
        return data.getvalue()

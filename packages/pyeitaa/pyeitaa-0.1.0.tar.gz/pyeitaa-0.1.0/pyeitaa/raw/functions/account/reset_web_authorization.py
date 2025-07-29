from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class ResetWebAuthorization(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x2d01b9ef``

    Parameters:
        hash: ``int`` ``64-bit``

    Returns:
        ``bool``
    """

    __slots__: List[str] = ["hash"]

    ID = 0x2d01b9ef
    QUALNAME = "functions.account.ResetWebAuthorization"

    def __init__(self, *, hash: int) -> None:
        self.hash = hash  # long

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        hash = Long.read(data)
        
        return ResetWebAuthorization(hash=hash)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Long(self.hash))
        
        return data.getvalue()

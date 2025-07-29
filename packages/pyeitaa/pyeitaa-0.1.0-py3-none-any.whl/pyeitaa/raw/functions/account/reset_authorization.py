from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class ResetAuthorization(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x20880c44``

    Parameters:
        hash: ``int`` ``64-bit``

    Returns:
        ``bool``
    """

    __slots__: List[str] = ["hash"]

    ID = -0x20880c44
    QUALNAME = "functions.account.ResetAuthorization"

    def __init__(self, *, hash: int) -> None:
        self.hash = hash  # long

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        hash = Long.read(data)
        
        return ResetAuthorization(hash=hash)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Long(self.hash))
        
        return data.getvalue()

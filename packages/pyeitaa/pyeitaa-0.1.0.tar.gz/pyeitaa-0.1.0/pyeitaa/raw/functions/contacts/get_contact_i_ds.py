from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class GetContactIDs(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x7adc669d``

    Parameters:
        hash: ``int`` ``64-bit``

    Returns:
        List of ``int`` ``32-bit``
    """

    __slots__: List[str] = ["hash"]

    ID = 0x7adc669d
    QUALNAME = "functions.contacts.GetContactIDs"

    def __init__(self, *, hash: int) -> None:
        self.hash = hash  # long

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        hash = Long.read(data)
        
        return GetContactIDs(hash=hash)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Long(self.hash))
        
        return data.getvalue()

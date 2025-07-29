from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String, Vector
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class DeleteByPhones(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x1013fd9e``

    Parameters:
        phones: List of ``str``

    Returns:
        ``bool``
    """

    __slots__: List[str] = ["phones"]

    ID = 0x1013fd9e
    QUALNAME = "functions.contacts.DeleteByPhones"

    def __init__(self, *, phones: List[str]) -> None:
        self.phones = phones  # Vector<string>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        phones = TLObject.read(data, String)
        
        return DeleteByPhones(phones=phones)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Vector(self.phones, String))
        
        return data.getvalue()

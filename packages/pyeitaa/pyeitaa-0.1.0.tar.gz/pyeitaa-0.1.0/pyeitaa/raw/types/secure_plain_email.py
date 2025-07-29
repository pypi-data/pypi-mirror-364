from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class SecurePlainEmail(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.SecurePlainData`.

    Details:
        - Layer: ``135``
        - ID: ``0x21ec5a5f``

    Parameters:
        email: ``str``
    """

    __slots__: List[str] = ["email"]

    ID = 0x21ec5a5f
    QUALNAME = "types.SecurePlainEmail"

    def __init__(self, *, email: str) -> None:
        self.email = email  # string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        email = String.read(data)
        
        return SecurePlainEmail(email=email)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(String(self.email))
        
        return data.getvalue()

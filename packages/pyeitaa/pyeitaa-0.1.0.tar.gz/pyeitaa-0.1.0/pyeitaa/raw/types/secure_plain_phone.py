from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class SecurePlainPhone(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.SecurePlainData`.

    Details:
        - Layer: ``135``
        - ID: ``0x7d6099dd``

    Parameters:
        phone: ``str``
    """

    __slots__: List[str] = ["phone"]

    ID = 0x7d6099dd
    QUALNAME = "types.SecurePlainPhone"

    def __init__(self, *, phone: str) -> None:
        self.phone = phone  # string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        phone = String.read(data)
        
        return SecurePlainPhone(phone=phone)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(String(self.phone))
        
        return data.getvalue()

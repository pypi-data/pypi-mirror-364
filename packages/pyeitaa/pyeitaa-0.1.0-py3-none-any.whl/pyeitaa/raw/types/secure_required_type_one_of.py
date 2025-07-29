from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class SecureRequiredTypeOneOf(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.SecureRequiredType`.

    Details:
        - Layer: ``135``
        - ID: ``0x27477b4``

    Parameters:
        types: List of :obj:`SecureRequiredType <pyeitaa.raw.base.SecureRequiredType>`
    """

    __slots__: List[str] = ["types"]

    ID = 0x27477b4
    QUALNAME = "types.SecureRequiredTypeOneOf"

    def __init__(self, *, types: List["raw.base.SecureRequiredType"]) -> None:
        self.types = types  # Vector<SecureRequiredType>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        types = TLObject.read(data)
        
        return SecureRequiredTypeOneOf(types=types)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Vector(self.types))
        
        return data.getvalue()

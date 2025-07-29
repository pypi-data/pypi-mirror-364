from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class MessageActionSecureValuesSent(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.MessageAction`.

    Details:
        - Layer: ``135``
        - ID: ``-0x26a39eac``

    Parameters:
        types: List of :obj:`SecureValueType <pyeitaa.raw.base.SecureValueType>`
    """

    __slots__: List[str] = ["types"]

    ID = -0x26a39eac
    QUALNAME = "types.MessageActionSecureValuesSent"

    def __init__(self, *, types: List["raw.base.SecureValueType"]) -> None:
        self.types = types  # Vector<SecureValueType>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        types = TLObject.read(data)
        
        return MessageActionSecureValuesSent(types=types)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Vector(self.types))
        
        return data.getvalue()

from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class DeleteSecureValue(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x477f43b5``

    Parameters:
        types: List of :obj:`SecureValueType <pyeitaa.raw.base.SecureValueType>`

    Returns:
        ``bool``
    """

    __slots__: List[str] = ["types"]

    ID = -0x477f43b5
    QUALNAME = "functions.account.DeleteSecureValue"

    def __init__(self, *, types: List["raw.base.SecureValueType"]) -> None:
        self.types = types  # Vector<SecureValueType>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        types = TLObject.read(data)
        
        return DeleteSecureValue(types=types)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Vector(self.types))
        
        return data.getvalue()

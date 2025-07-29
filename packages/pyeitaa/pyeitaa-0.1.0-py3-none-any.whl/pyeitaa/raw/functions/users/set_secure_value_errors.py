from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class SetSecureValueErrors(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x6f376b4b``

    Parameters:
        id: :obj:`InputUser <pyeitaa.raw.base.InputUser>`
        errors: List of :obj:`SecureValueError <pyeitaa.raw.base.SecureValueError>`

    Returns:
        ``bool``
    """

    __slots__: List[str] = ["id", "errors"]

    ID = -0x6f376b4b
    QUALNAME = "functions.users.SetSecureValueErrors"

    def __init__(self, *, id: "raw.base.InputUser", errors: List["raw.base.SecureValueError"]) -> None:
        self.id = id  # InputUser
        self.errors = errors  # Vector<SecureValueError>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        id = TLObject.read(data)
        
        errors = TLObject.read(data)
        
        return SetSecureValueErrors(id=id, errors=errors)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.id.write())
        
        data.write(Vector(self.errors))
        
        return data.getvalue()

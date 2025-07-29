from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class DeleteContacts(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x96a0e00``

    Parameters:
        id: List of :obj:`InputUser <pyeitaa.raw.base.InputUser>`

    Returns:
        :obj:`Updates <pyeitaa.raw.base.Updates>`
    """

    __slots__: List[str] = ["id"]

    ID = 0x96a0e00
    QUALNAME = "functions.contacts.DeleteContacts"

    def __init__(self, *, id: List["raw.base.InputUser"]) -> None:
        self.id = id  # Vector<InputUser>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        id = TLObject.read(data)
        
        return DeleteContacts(id=id)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Vector(self.id))
        
        return data.getvalue()

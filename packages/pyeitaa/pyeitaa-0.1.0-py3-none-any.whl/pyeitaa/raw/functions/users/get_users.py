from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class GetUsers(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0xd91a548``

    Parameters:
        id: List of :obj:`InputUser <pyeitaa.raw.base.InputUser>`

    Returns:
        List of :obj:`User <pyeitaa.raw.base.User>`
    """

    __slots__: List[str] = ["id"]

    ID = 0xd91a548
    QUALNAME = "functions.users.GetUsers"

    def __init__(self, *, id: List["raw.base.InputUser"]) -> None:
        self.id = id  # Vector<InputUser>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        id = TLObject.read(data)
        
        return GetUsers(id=id)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Vector(self.id))
        
        return data.getvalue()

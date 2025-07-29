from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class GetFullUser(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x35cf5a4f``

    Parameters:
        id: :obj:`InputUser <pyeitaa.raw.base.InputUser>`

    Returns:
        :obj:`UserFull <pyeitaa.raw.base.UserFull>`
    """

    __slots__: List[str] = ["id"]

    ID = -0x35cf5a4f
    QUALNAME = "functions.users.GetFullUser"

    def __init__(self, *, id: "raw.base.InputUser") -> None:
        self.id = id  # InputUser

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        id = TLObject.read(data)
        
        return GetFullUser(id=id)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.id.write())
        
        return data.getvalue()

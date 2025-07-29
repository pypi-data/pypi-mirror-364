from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class GetUserInfo(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x38a08d3``

    Parameters:
        user_id: :obj:`InputUser <pyeitaa.raw.base.InputUser>`

    Returns:
        :obj:`help.UserInfo <pyeitaa.raw.base.help.UserInfo>`
    """

    __slots__: List[str] = ["user_id"]

    ID = 0x38a08d3
    QUALNAME = "functions.help.GetUserInfo"

    def __init__(self, *, user_id: "raw.base.InputUser") -> None:
        self.user_id = user_id  # InputUser

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        user_id = TLObject.read(data)
        
        return GetUserInfo(user_id=user_id)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.user_id.write())
        
        return data.getvalue()

from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class InviteToGroupCall(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x7b393160``

    Parameters:
        call: :obj:`InputGroupCall <pyeitaa.raw.base.InputGroupCall>`
        users: List of :obj:`InputUser <pyeitaa.raw.base.InputUser>`

    Returns:
        :obj:`Updates <pyeitaa.raw.base.Updates>`
    """

    __slots__: List[str] = ["call", "users"]

    ID = 0x7b393160
    QUALNAME = "functions.phone.InviteToGroupCall"

    def __init__(self, *, call: "raw.base.InputGroupCall", users: List["raw.base.InputUser"]) -> None:
        self.call = call  # InputGroupCall
        self.users = users  # Vector<InputUser>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        call = TLObject.read(data)
        
        users = TLObject.read(data)
        
        return InviteToGroupCall(call=call, users=users)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.call.write())
        
        data.write(Vector(self.users))
        
        return data.getvalue()

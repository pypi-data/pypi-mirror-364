from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class MessageActionInviteToGroupCall(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.MessageAction`.

    Details:
        - Layer: ``135``
        - ID: ``0x502f92f7``

    Parameters:
        call: :obj:`InputGroupCall <pyeitaa.raw.base.InputGroupCall>`
        users: List of ``int`` ``64-bit``
    """

    __slots__: List[str] = ["call", "users"]

    ID = 0x502f92f7
    QUALNAME = "types.MessageActionInviteToGroupCall"

    def __init__(self, *, call: "raw.base.InputGroupCall", users: List[int]) -> None:
        self.call = call  # InputGroupCall
        self.users = users  # Vector<long>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        call = TLObject.read(data)
        
        users = TLObject.read(data, Long)
        
        return MessageActionInviteToGroupCall(call=call, users=users)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.call.write())
        
        data.write(Vector(self.users, Long))
        
        return data.getvalue()

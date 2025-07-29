from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class InviteToChannel(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x199f3a6c``

    Parameters:
        channel: :obj:`InputChannel <pyeitaa.raw.base.InputChannel>`
        users: List of :obj:`InputUser <pyeitaa.raw.base.InputUser>`

    Returns:
        :obj:`Updates <pyeitaa.raw.base.Updates>`
    """

    __slots__: List[str] = ["channel", "users"]

    ID = 0x199f3a6c
    QUALNAME = "functions.channels.InviteToChannel"

    def __init__(self, *, channel: "raw.base.InputChannel", users: List["raw.base.InputUser"]) -> None:
        self.channel = channel  # InputChannel
        self.users = users  # Vector<InputUser>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        channel = TLObject.read(data)
        
        users = TLObject.read(data)
        
        return InviteToChannel(channel=channel, users=users)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.channel.write())
        
        data.write(Vector(self.users))
        
        return data.getvalue()

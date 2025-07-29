from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class BotCommandScopePeerUser(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.BotCommandScope`.

    Details:
        - Layer: ``135``
        - ID: ``0xa1321f3``

    Parameters:
        peer: :obj:`InputPeer <pyeitaa.raw.base.InputPeer>`
        user_id: :obj:`InputUser <pyeitaa.raw.base.InputUser>`
    """

    __slots__: List[str] = ["peer", "user_id"]

    ID = 0xa1321f3
    QUALNAME = "types.BotCommandScopePeerUser"

    def __init__(self, *, peer: "raw.base.InputPeer", user_id: "raw.base.InputUser") -> None:
        self.peer = peer  # InputPeer
        self.user_id = user_id  # InputUser

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        peer = TLObject.read(data)
        
        user_id = TLObject.read(data)
        
        return BotCommandScopePeerUser(peer=peer, user_id=user_id)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.peer.write())
        
        data.write(self.user_id.write())
        
        return data.getvalue()

from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class InputPeerUserFromMessage(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.InputPeer`.

    Details:
        - Layer: ``135``
        - ID: ``-0x5784f5e4``

    Parameters:
        peer: :obj:`InputPeer <pyeitaa.raw.base.InputPeer>`
        msg_id: ``int`` ``32-bit``
        user_id: ``int`` ``64-bit``
    """

    __slots__: List[str] = ["peer", "msg_id", "user_id"]

    ID = -0x5784f5e4
    QUALNAME = "types.InputPeerUserFromMessage"

    def __init__(self, *, peer: "raw.base.InputPeer", msg_id: int, user_id: int) -> None:
        self.peer = peer  # InputPeer
        self.msg_id = msg_id  # int
        self.user_id = user_id  # long

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        peer = TLObject.read(data)
        
        msg_id = Int.read(data)
        
        user_id = Long.read(data)
        
        return InputPeerUserFromMessage(peer=peer, msg_id=msg_id, user_id=user_id)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.peer.write())
        
        data.write(Int(self.msg_id))
        
        data.write(Long(self.user_id))
        
        return data.getvalue()

from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class SendScheduledMessages(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x42c77af6``

    Parameters:
        peer: :obj:`InputPeer <pyeitaa.raw.base.InputPeer>`
        id: List of ``int`` ``32-bit``

    Returns:
        :obj:`Updates <pyeitaa.raw.base.Updates>`
    """

    __slots__: List[str] = ["peer", "id"]

    ID = -0x42c77af6
    QUALNAME = "functions.messages.SendScheduledMessages"

    def __init__(self, *, peer: "raw.base.InputPeer", id: List[int]) -> None:
        self.peer = peer  # InputPeer
        self.id = id  # Vector<int>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        peer = TLObject.read(data)
        
        id = TLObject.read(data, Int)
        
        return SendScheduledMessages(peer=peer, id=id)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.peer.write())
        
        data.write(Vector(self.id, Int))
        
        return data.getvalue()

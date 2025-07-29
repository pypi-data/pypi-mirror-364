from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class DeleteScheduledMessages(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x59ae2b16``

    Parameters:
        peer: :obj:`InputPeer <pyeitaa.raw.base.InputPeer>`
        id: List of ``int`` ``32-bit``

    Returns:
        :obj:`Updates <pyeitaa.raw.base.Updates>`
    """

    __slots__: List[str] = ["peer", "id"]

    ID = 0x59ae2b16
    QUALNAME = "functions.messages.DeleteScheduledMessages"

    def __init__(self, *, peer: "raw.base.InputPeer", id: List[int]) -> None:
        self.peer = peer  # InputPeer
        self.id = id  # Vector<int>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        peer = TLObject.read(data)
        
        id = TLObject.read(data, Int)
        
        return DeleteScheduledMessages(peer=peer, id=id)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.peer.write())
        
        data.write(Vector(self.id, Int))
        
        return data.getvalue()

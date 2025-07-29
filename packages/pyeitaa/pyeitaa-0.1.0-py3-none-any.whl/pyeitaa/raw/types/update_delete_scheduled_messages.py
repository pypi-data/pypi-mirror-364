from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class UpdateDeleteScheduledMessages(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.Update`.

    Details:
        - Layer: ``135``
        - ID: ``-0x6f799312``

    Parameters:
        peer: :obj:`Peer <pyeitaa.raw.base.Peer>`
        messages: List of ``int`` ``32-bit``
    """

    __slots__: List[str] = ["peer", "messages"]

    ID = -0x6f799312
    QUALNAME = "types.UpdateDeleteScheduledMessages"

    def __init__(self, *, peer: "raw.base.Peer", messages: List[int]) -> None:
        self.peer = peer  # Peer
        self.messages = messages  # Vector<int>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        peer = TLObject.read(data)
        
        messages = TLObject.read(data, Int)
        
        return UpdateDeleteScheduledMessages(peer=peer, messages=messages)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.peer.write())
        
        data.write(Vector(self.messages, Int))
        
        return data.getvalue()

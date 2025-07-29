from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Bool, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class GetMessagesViews(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x5784d3e1``

    Parameters:
        peer: :obj:`InputPeer <pyeitaa.raw.base.InputPeer>`
        id: List of ``int`` ``32-bit``
        increment: ``bool``

    Returns:
        :obj:`messages.MessageViews <pyeitaa.raw.base.messages.MessageViews>`
    """

    __slots__: List[str] = ["peer", "id", "increment"]

    ID = 0x5784d3e1
    QUALNAME = "functions.messages.GetMessagesViews"

    def __init__(self, *, peer: "raw.base.InputPeer", id: List[int], increment: bool) -> None:
        self.peer = peer  # InputPeer
        self.id = id  # Vector<int>
        self.increment = increment  # Bool

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        peer = TLObject.read(data)
        
        id = TLObject.read(data, Int)
        
        increment = Bool.read(data)
        
        return GetMessagesViews(peer=peer, id=id, increment=increment)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        
        data.write(Int(flags))
        
        data.write(self.peer.write())
        
        data.write(Vector(self.id, Int))
        
        data.write(Bool(self.increment))
        
        return data.getvalue()

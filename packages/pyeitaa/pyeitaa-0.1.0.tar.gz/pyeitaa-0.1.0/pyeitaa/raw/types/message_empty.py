from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class MessageEmpty(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.Message`.

    Details:
        - Layer: ``135``
        - ID: ``-0x6f59357c``

    Parameters:
        id: ``int`` ``32-bit``
        peer_id (optional): :obj:`Peer <pyeitaa.raw.base.Peer>`
    """

    __slots__: List[str] = ["id", "peer_id"]

    ID = -0x6f59357c
    QUALNAME = "types.MessageEmpty"

    def __init__(self, *, id: int, peer_id: "raw.base.Peer" = None) -> None:
        self.id = id  # int
        self.peer_id = peer_id  # flags.0?Peer

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        id = Int.read(data)
        
        peer_id = TLObject.read(data) if flags & (1 << 0) else None
        
        return MessageEmpty(id=id, peer_id=peer_id)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.peer_id is not None else 0
        data.write(Int(flags))
        
        data.write(Int(self.id))
        
        if self.peer_id is not None:
            data.write(self.peer_id.write())
        
        return data.getvalue()

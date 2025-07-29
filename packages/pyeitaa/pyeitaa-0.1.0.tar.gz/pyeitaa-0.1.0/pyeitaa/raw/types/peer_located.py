from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class PeerLocated(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.PeerLocated`.

    Details:
        - Layer: ``135``
        - ID: ``-0x35b9e4a3``

    Parameters:
        peer: :obj:`Peer <pyeitaa.raw.base.Peer>`
        expires: ``int`` ``32-bit``
        distance: ``int`` ``32-bit``
    """

    __slots__: List[str] = ["peer", "expires", "distance"]

    ID = -0x35b9e4a3
    QUALNAME = "types.PeerLocated"

    def __init__(self, *, peer: "raw.base.Peer", expires: int, distance: int) -> None:
        self.peer = peer  # Peer
        self.expires = expires  # int
        self.distance = distance  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        peer = TLObject.read(data)
        
        expires = Int.read(data)
        
        distance = Int.read(data)
        
        return PeerLocated(peer=peer, expires=expires, distance=distance)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.peer.write())
        
        data.write(Int(self.expires))
        
        data.write(Int(self.distance))
        
        return data.getvalue()

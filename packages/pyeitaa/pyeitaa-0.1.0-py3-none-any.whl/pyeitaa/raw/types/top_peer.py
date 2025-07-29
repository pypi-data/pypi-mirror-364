from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Double
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class TopPeer(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.TopPeer`.

    Details:
        - Layer: ``135``
        - ID: ``-0x12323fa5``

    Parameters:
        peer: :obj:`Peer <pyeitaa.raw.base.Peer>`
        rating: ``float`` ``64-bit``
    """

    __slots__: List[str] = ["peer", "rating"]

    ID = -0x12323fa5
    QUALNAME = "types.TopPeer"

    def __init__(self, *, peer: "raw.base.Peer", rating: float) -> None:
        self.peer = peer  # Peer
        self.rating = rating  # double

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        peer = TLObject.read(data)
        
        rating = Double.read(data)
        
        return TopPeer(peer=peer, rating=rating)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.peer.write())
        
        data.write(Double(self.rating))
        
        return data.getvalue()

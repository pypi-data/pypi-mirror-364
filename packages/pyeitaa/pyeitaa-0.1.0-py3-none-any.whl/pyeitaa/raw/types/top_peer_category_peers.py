from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class TopPeerCategoryPeers(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.TopPeerCategoryPeers`.

    Details:
        - Layer: ``135``
        - ID: ``-0x47cbd6f``

    Parameters:
        category: :obj:`TopPeerCategory <pyeitaa.raw.base.TopPeerCategory>`
        count: ``int`` ``32-bit``
        peers: List of :obj:`TopPeer <pyeitaa.raw.base.TopPeer>`
    """

    __slots__: List[str] = ["category", "count", "peers"]

    ID = -0x47cbd6f
    QUALNAME = "types.TopPeerCategoryPeers"

    def __init__(self, *, category: "raw.base.TopPeerCategory", count: int, peers: List["raw.base.TopPeer"]) -> None:
        self.category = category  # TopPeerCategory
        self.count = count  # int
        self.peers = peers  # Vector<TopPeer>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        category = TLObject.read(data)
        
        count = Int.read(data)
        
        peers = TLObject.read(data)
        
        return TopPeerCategoryPeers(category=category, count=count, peers=peers)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.category.write())
        
        data.write(Int(self.count))
        
        data.write(Vector(self.peers))
        
        return data.getvalue()

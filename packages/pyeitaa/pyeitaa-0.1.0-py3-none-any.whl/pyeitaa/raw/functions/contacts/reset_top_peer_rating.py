from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class ResetTopPeerRating(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x1ae373ac``

    Parameters:
        category: :obj:`TopPeerCategory <pyeitaa.raw.base.TopPeerCategory>`
        peer: :obj:`InputPeer <pyeitaa.raw.base.InputPeer>`

    Returns:
        ``bool``
    """

    __slots__: List[str] = ["category", "peer"]

    ID = 0x1ae373ac
    QUALNAME = "functions.contacts.ResetTopPeerRating"

    def __init__(self, *, category: "raw.base.TopPeerCategory", peer: "raw.base.InputPeer") -> None:
        self.category = category  # TopPeerCategory
        self.peer = peer  # InputPeer

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        category = TLObject.read(data)
        
        peer = TLObject.read(data)
        
        return ResetTopPeerRating(category=category, peer=peer)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.category.write())
        
        data.write(self.peer.write())
        
        return data.getvalue()

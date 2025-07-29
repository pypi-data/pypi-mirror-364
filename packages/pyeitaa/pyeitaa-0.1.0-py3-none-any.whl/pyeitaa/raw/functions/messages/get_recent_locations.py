from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class GetRecentLocations(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x702a40e0``

    Parameters:
        peer: :obj:`InputPeer <pyeitaa.raw.base.InputPeer>`
        limit: ``int`` ``32-bit``
        hash: ``int`` ``64-bit``

    Returns:
        :obj:`messages.Messages <pyeitaa.raw.base.messages.Messages>`
    """

    __slots__: List[str] = ["peer", "limit", "hash"]

    ID = 0x702a40e0
    QUALNAME = "functions.messages.GetRecentLocations"

    def __init__(self, *, peer: "raw.base.InputPeer", limit: int, hash: int) -> None:
        self.peer = peer  # InputPeer
        self.limit = limit  # int
        self.hash = hash  # long

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        peer = TLObject.read(data)
        
        limit = Int.read(data)
        
        hash = Long.read(data)
        
        return GetRecentLocations(peer=peer, limit=limit, hash=hash)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.peer.write())
        
        data.write(Int(self.limit))
        
        data.write(Long(self.hash))
        
        return data.getvalue()

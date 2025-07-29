from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class UpdatePeerHistoryTTL(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.Update`.

    Details:
        - Layer: ``135``
        - ID: ``-0x4464465b``

    Parameters:
        peer: :obj:`Peer <pyeitaa.raw.base.Peer>`
        ttl_period (optional): ``int`` ``32-bit``
    """

    __slots__: List[str] = ["peer", "ttl_period"]

    ID = -0x4464465b
    QUALNAME = "types.UpdatePeerHistoryTTL"

    def __init__(self, *, peer: "raw.base.Peer", ttl_period: Optional[int] = None) -> None:
        self.peer = peer  # Peer
        self.ttl_period = ttl_period  # flags.0?int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        peer = TLObject.read(data)
        
        ttl_period = Int.read(data) if flags & (1 << 0) else None
        return UpdatePeerHistoryTTL(peer=peer, ttl_period=ttl_period)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.ttl_period is not None else 0
        data.write(Int(flags))
        
        data.write(self.peer.write())
        
        if self.ttl_period is not None:
            data.write(Int(self.ttl_period))
        
        return data.getvalue()

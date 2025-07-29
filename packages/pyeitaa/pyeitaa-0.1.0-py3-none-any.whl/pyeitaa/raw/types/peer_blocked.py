from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class PeerBlocked(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.PeerBlocked`.

    Details:
        - Layer: ``135``
        - ID: ``-0x17027fec``

    Parameters:
        peer_id: :obj:`Peer <pyeitaa.raw.base.Peer>`
        date: ``int`` ``32-bit``
    """

    __slots__: List[str] = ["peer_id", "date"]

    ID = -0x17027fec
    QUALNAME = "types.PeerBlocked"

    def __init__(self, *, peer_id: "raw.base.Peer", date: int) -> None:
        self.peer_id = peer_id  # Peer
        self.date = date  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        peer_id = TLObject.read(data)
        
        date = Int.read(data)
        
        return PeerBlocked(peer_id=peer_id, date=date)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.peer_id.write())
        
        data.write(Int(self.date))
        
        return data.getvalue()

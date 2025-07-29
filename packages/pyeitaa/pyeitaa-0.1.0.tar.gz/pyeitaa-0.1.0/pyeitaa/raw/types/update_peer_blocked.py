from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Bool
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class UpdatePeerBlocked(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.Update`.

    Details:
        - Layer: ``135``
        - ID: ``0x246a4b22``

    Parameters:
        peer_id: :obj:`Peer <pyeitaa.raw.base.Peer>`
        blocked: ``bool``
    """

    __slots__: List[str] = ["peer_id", "blocked"]

    ID = 0x246a4b22
    QUALNAME = "types.UpdatePeerBlocked"

    def __init__(self, *, peer_id: "raw.base.Peer", blocked: bool) -> None:
        self.peer_id = peer_id  # Peer
        self.blocked = blocked  # Bool

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        peer_id = TLObject.read(data)
        
        blocked = Bool.read(data)
        
        return UpdatePeerBlocked(peer_id=peer_id, blocked=blocked)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.peer_id.write())
        
        data.write(Bool(self.blocked))
        
        return data.getvalue()

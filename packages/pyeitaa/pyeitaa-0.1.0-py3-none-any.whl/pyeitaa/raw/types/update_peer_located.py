from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class UpdatePeerLocated(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.Update`.

    Details:
        - Layer: ``135``
        - ID: ``-0x4b503050``

    Parameters:
        peers: List of :obj:`PeerLocated <pyeitaa.raw.base.PeerLocated>`
    """

    __slots__: List[str] = ["peers"]

    ID = -0x4b503050
    QUALNAME = "types.UpdatePeerLocated"

    def __init__(self, *, peers: List["raw.base.PeerLocated"]) -> None:
        self.peers = peers  # Vector<PeerLocated>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        peers = TLObject.read(data)
        
        return UpdatePeerLocated(peers=peers)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Vector(self.peers))
        
        return data.getvalue()

from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class UpdatePeerSettings(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.Update`.

    Details:
        - Layer: ``135``
        - ID: ``0x6a7e7366``

    Parameters:
        peer: :obj:`Peer <pyeitaa.raw.base.Peer>`
        settings: :obj:`PeerSettings <pyeitaa.raw.base.PeerSettings>`
    """

    __slots__: List[str] = ["peer", "settings"]

    ID = 0x6a7e7366
    QUALNAME = "types.UpdatePeerSettings"

    def __init__(self, *, peer: "raw.base.Peer", settings: "raw.base.PeerSettings") -> None:
        self.peer = peer  # Peer
        self.settings = settings  # PeerSettings

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        peer = TLObject.read(data)
        
        settings = TLObject.read(data)
        
        return UpdatePeerSettings(peer=peer, settings=settings)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.peer.write())
        
        data.write(self.settings.write())
        
        return data.getvalue()

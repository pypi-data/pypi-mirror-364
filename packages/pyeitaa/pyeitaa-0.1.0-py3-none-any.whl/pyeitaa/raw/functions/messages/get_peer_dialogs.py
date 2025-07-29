from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class GetPeerDialogs(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x1b8f4303``

    Parameters:
        peers: List of :obj:`InputPeer <pyeitaa.raw.base.InputPeer>`

    Returns:
        :obj:`messages.PeerDialogs <pyeitaa.raw.base.messages.PeerDialogs>`
    """

    __slots__: List[str] = ["peers"]

    ID = -0x1b8f4303
    QUALNAME = "functions.messages.GetPeerDialogs"

    def __init__(self, *, peers: List["raw.base.InputPeer"]) -> None:
        self.peers = peers  # Vector<InputPeer>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        peers = TLObject.read(data)
        
        return GetPeerDialogs(peers=peers)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Vector(self.peers))
        
        return data.getvalue()

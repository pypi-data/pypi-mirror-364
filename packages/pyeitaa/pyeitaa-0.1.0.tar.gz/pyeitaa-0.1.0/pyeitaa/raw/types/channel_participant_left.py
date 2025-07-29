from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class ChannelParticipantLeft(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.ChannelParticipant`.

    Details:
        - Layer: ``135``
        - ID: ``0x1b03f006``

    Parameters:
        peer: :obj:`Peer <pyeitaa.raw.base.Peer>`
    """

    __slots__: List[str] = ["peer"]

    ID = 0x1b03f006
    QUALNAME = "types.ChannelParticipantLeft"

    def __init__(self, *, peer: "raw.base.Peer") -> None:
        self.peer = peer  # Peer

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        peer = TLObject.read(data)
        
        return ChannelParticipantLeft(peer=peer)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.peer.write())
        
        return data.getvalue()

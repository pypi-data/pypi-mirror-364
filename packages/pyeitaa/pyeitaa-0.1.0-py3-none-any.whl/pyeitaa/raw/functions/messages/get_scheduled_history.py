from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class GetScheduledHistory(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0xae989f5``

    Parameters:
        peer: :obj:`InputPeer <pyeitaa.raw.base.InputPeer>`
        hash: ``int`` ``64-bit``

    Returns:
        :obj:`messages.Messages <pyeitaa.raw.base.messages.Messages>`
    """

    __slots__: List[str] = ["peer", "hash"]

    ID = -0xae989f5
    QUALNAME = "functions.messages.GetScheduledHistory"

    def __init__(self, *, peer: "raw.base.InputPeer", hash: int) -> None:
        self.peer = peer  # InputPeer
        self.hash = hash  # long

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        peer = TLObject.read(data)
        
        hash = Long.read(data)
        
        return GetScheduledHistory(peer=peer, hash=hash)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.peer.write())
        
        data.write(Long(self.hash))
        
        return data.getvalue()

from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class ReadHistory(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0xe306d3a``

    Parameters:
        peer: :obj:`InputPeer <pyeitaa.raw.base.InputPeer>`
        max_id: ``int`` ``32-bit``

    Returns:
        :obj:`messages.AffectedMessages <pyeitaa.raw.base.messages.AffectedMessages>`
    """

    __slots__: List[str] = ["peer", "max_id"]

    ID = 0xe306d3a
    QUALNAME = "functions.messages.ReadHistory"

    def __init__(self, *, peer: "raw.base.InputPeer", max_id: int) -> None:
        self.peer = peer  # InputPeer
        self.max_id = max_id  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        peer = TLObject.read(data)
        
        max_id = Int.read(data)
        
        return ReadHistory(peer=peer, max_id=max_id)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.peer.write())
        
        data.write(Int(self.max_id))
        
        return data.getvalue()

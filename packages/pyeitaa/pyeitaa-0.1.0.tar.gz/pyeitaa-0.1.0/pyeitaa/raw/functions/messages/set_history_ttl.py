from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class SetHistoryTTL(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x47f1a01c``

    Parameters:
        peer: :obj:`InputPeer <pyeitaa.raw.base.InputPeer>`
        period: ``int`` ``32-bit``

    Returns:
        :obj:`Updates <pyeitaa.raw.base.Updates>`
    """

    __slots__: List[str] = ["peer", "period"]

    ID = -0x47f1a01c
    QUALNAME = "functions.messages.SetHistoryTTL"

    def __init__(self, *, peer: "raw.base.InputPeer", period: int) -> None:
        self.peer = peer  # InputPeer
        self.period = period  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        peer = TLObject.read(data)
        
        period = Int.read(data)
        
        return SetHistoryTTL(peer=peer, period=period)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.peer.write())
        
        data.write(Int(self.period))
        
        return data.getvalue()

from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class GetSearchCounters(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x732eef00``

    Parameters:
        peer: :obj:`InputPeer <pyeitaa.raw.base.InputPeer>`
        filters: List of :obj:`MessagesFilter <pyeitaa.raw.base.MessagesFilter>`

    Returns:
        List of :obj:`messages.SearchCounter <pyeitaa.raw.base.messages.SearchCounter>`
    """

    __slots__: List[str] = ["peer", "filters"]

    ID = 0x732eef00
    QUALNAME = "functions.messages.GetSearchCounters"

    def __init__(self, *, peer: "raw.base.InputPeer", filters: List["raw.base.MessagesFilter"]) -> None:
        self.peer = peer  # InputPeer
        self.filters = filters  # Vector<MessagesFilter>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        peer = TLObject.read(data)
        
        filters = TLObject.read(data)
        
        return GetSearchCounters(peer=peer, filters=filters)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.peer.write())
        
        data.write(Vector(self.filters))
        
        return data.getvalue()

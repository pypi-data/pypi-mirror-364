from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class SearchGlobalExt(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x2a6cac10``

    Parameters:
        q: ``str``
        offset_date: ``int`` ``32-bit``
        offset_peer: :obj:`InputPeer <pyeitaa.raw.base.InputPeer>`
        offset_id: ``int`` ``32-bit``
        limit: ``int`` ``32-bit``

    Returns:
        :obj:`messages.Messages <pyeitaa.raw.base.messages.Messages>`
    """

    __slots__: List[str] = ["q", "offset_date", "offset_peer", "offset_id", "limit"]

    ID = 0x2a6cac10
    QUALNAME = "functions.messages.SearchGlobalExt"

    def __init__(self, *, q: str, offset_date: int, offset_peer: "raw.base.InputPeer", offset_id: int, limit: int) -> None:
        self.q = q  # string
        self.offset_date = offset_date  # int
        self.offset_peer = offset_peer  # InputPeer
        self.offset_id = offset_id  # int
        self.limit = limit  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        q = String.read(data)
        
        offset_date = Int.read(data)
        
        offset_peer = TLObject.read(data)
        
        offset_id = Int.read(data)
        
        limit = Int.read(data)
        
        return SearchGlobalExt(q=q, offset_date=offset_date, offset_peer=offset_peer, offset_id=offset_id, limit=limit)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        
        data.write(Int(flags))
        
        data.write(String(self.q))
        
        data.write(Int(self.offset_date))
        
        data.write(self.offset_peer.write())
        
        data.write(Int(self.offset_id))
        
        data.write(Int(self.limit))
        
        return data.getvalue()

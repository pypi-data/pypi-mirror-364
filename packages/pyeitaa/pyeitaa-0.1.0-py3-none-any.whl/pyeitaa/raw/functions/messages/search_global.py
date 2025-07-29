from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class SearchGlobal(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x4bc6589a``

    Parameters:
        q: ``str``
        filter: :obj:`MessagesFilter <pyeitaa.raw.base.MessagesFilter>`
        min_date: ``int`` ``32-bit``
        max_date: ``int`` ``32-bit``
        offset_rate: ``int`` ``32-bit``
        offset_peer: :obj:`InputPeer <pyeitaa.raw.base.InputPeer>`
        offset_id: ``int`` ``32-bit``
        limit: ``int`` ``32-bit``
        folder_id (optional): ``int`` ``32-bit``

    Returns:
        :obj:`messages.Messages <pyeitaa.raw.base.messages.Messages>`
    """

    __slots__: List[str] = ["q", "filter", "min_date", "max_date", "offset_rate", "offset_peer", "offset_id", "limit", "folder_id"]

    ID = 0x4bc6589a
    QUALNAME = "functions.messages.SearchGlobal"

    def __init__(self, *, q: str, filter: "raw.base.MessagesFilter", min_date: int, max_date: int, offset_rate: int, offset_peer: "raw.base.InputPeer", offset_id: int, limit: int, folder_id: Optional[int] = None) -> None:
        self.q = q  # string
        self.filter = filter  # MessagesFilter
        self.min_date = min_date  # int
        self.max_date = max_date  # int
        self.offset_rate = offset_rate  # int
        self.offset_peer = offset_peer  # InputPeer
        self.offset_id = offset_id  # int
        self.limit = limit  # int
        self.folder_id = folder_id  # flags.0?int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        folder_id = Int.read(data) if flags & (1 << 0) else None
        q = String.read(data)
        
        filter = TLObject.read(data)
        
        min_date = Int.read(data)
        
        max_date = Int.read(data)
        
        offset_rate = Int.read(data)
        
        offset_peer = TLObject.read(data)
        
        offset_id = Int.read(data)
        
        limit = Int.read(data)
        
        return SearchGlobal(q=q, filter=filter, min_date=min_date, max_date=max_date, offset_rate=offset_rate, offset_peer=offset_peer, offset_id=offset_id, limit=limit, folder_id=folder_id)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.folder_id is not None else 0
        data.write(Int(flags))
        
        if self.folder_id is not None:
            data.write(Int(self.folder_id))
        
        data.write(String(self.q))
        
        data.write(self.filter.write())
        
        data.write(Int(self.min_date))
        
        data.write(Int(self.max_date))
        
        data.write(Int(self.offset_rate))
        
        data.write(self.offset_peer.write())
        
        data.write(Int(self.offset_id))
        
        data.write(Int(self.limit))
        
        return data.getvalue()

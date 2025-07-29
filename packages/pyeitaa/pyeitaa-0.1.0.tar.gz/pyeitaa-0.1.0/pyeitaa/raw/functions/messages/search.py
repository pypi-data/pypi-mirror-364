from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, String
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class Search(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x5f02589e``

    Parameters:
        peer: :obj:`InputPeer <pyeitaa.raw.base.InputPeer>`
        q: ``str``
        filter: :obj:`MessagesFilter <pyeitaa.raw.base.MessagesFilter>`
        min_date: ``int`` ``32-bit``
        max_date: ``int`` ``32-bit``
        offset_id: ``int`` ``32-bit``
        add_offset: ``int`` ``32-bit``
        limit: ``int`` ``32-bit``
        max_id: ``int`` ``32-bit``
        min_id: ``int`` ``32-bit``
        hash: ``int`` ``64-bit``
        from_id (optional): :obj:`InputPeer <pyeitaa.raw.base.InputPeer>`
        top_msg_id (optional): ``int`` ``32-bit``

    Returns:
        :obj:`messages.Messages <pyeitaa.raw.base.messages.Messages>`
    """

    __slots__: List[str] = ["peer", "q", "filter", "min_date", "max_date", "offset_id", "add_offset", "limit", "max_id", "min_id", "hash", "from_id", "top_msg_id"]

    ID = -0x5f02589e
    QUALNAME = "functions.messages.Search"

    def __init__(self, *, peer: "raw.base.InputPeer", q: str, filter: "raw.base.MessagesFilter", min_date: int, max_date: int, offset_id: int, add_offset: int, limit: int, max_id: int, min_id: int, hash: int, from_id: "raw.base.InputPeer" = None, top_msg_id: Optional[int] = None) -> None:
        self.peer = peer  # InputPeer
        self.q = q  # string
        self.filter = filter  # MessagesFilter
        self.min_date = min_date  # int
        self.max_date = max_date  # int
        self.offset_id = offset_id  # int
        self.add_offset = add_offset  # int
        self.limit = limit  # int
        self.max_id = max_id  # int
        self.min_id = min_id  # int
        self.hash = hash  # long
        self.from_id = from_id  # flags.0?InputPeer
        self.top_msg_id = top_msg_id  # flags.1?int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        peer = TLObject.read(data)
        
        q = String.read(data)
        
        from_id = TLObject.read(data) if flags & (1 << 0) else None
        
        top_msg_id = Int.read(data) if flags & (1 << 1) else None
        filter = TLObject.read(data)
        
        min_date = Int.read(data)
        
        max_date = Int.read(data)
        
        offset_id = Int.read(data)
        
        add_offset = Int.read(data)
        
        limit = Int.read(data)
        
        max_id = Int.read(data)
        
        min_id = Int.read(data)
        
        hash = Long.read(data)
        
        return Search(peer=peer, q=q, filter=filter, min_date=min_date, max_date=max_date, offset_id=offset_id, add_offset=add_offset, limit=limit, max_id=max_id, min_id=min_id, hash=hash, from_id=from_id, top_msg_id=top_msg_id)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.from_id is not None else 0
        flags |= (1 << 1) if self.top_msg_id is not None else 0
        data.write(Int(flags))
        
        data.write(self.peer.write())
        
        data.write(String(self.q))
        
        if self.from_id is not None:
            data.write(self.from_id.write())
        
        if self.top_msg_id is not None:
            data.write(Int(self.top_msg_id))
        
        data.write(self.filter.write())
        
        data.write(Int(self.min_date))
        
        data.write(Int(self.max_date))
        
        data.write(Int(self.offset_id))
        
        data.write(Int(self.add_offset))
        
        data.write(Int(self.limit))
        
        data.write(Int(self.max_id))
        
        data.write(Int(self.min_id))
        
        data.write(Long(self.hash))
        
        return data.getvalue()

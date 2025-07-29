from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class GetHistory(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x4423e6c5``

    Parameters:
        peer: :obj:`InputPeer <pyeitaa.raw.base.InputPeer>`
        offset_id: ``int`` ``32-bit``
        offset_date: ``int`` ``32-bit``
        add_offset: ``int`` ``32-bit``
        limit: ``int`` ``32-bit``
        max_id: ``int`` ``32-bit``
        min_id: ``int`` ``32-bit``
        hash: ``int`` ``64-bit``

    Returns:
        :obj:`messages.Messages <pyeitaa.raw.base.messages.Messages>`
    """

    __slots__: List[str] = ["peer", "offset_id", "offset_date", "add_offset", "limit", "max_id", "min_id", "hash"]

    ID = 0x4423e6c5
    QUALNAME = "functions.messages.GetHistory"

    def __init__(self, *, peer: "raw.base.InputPeer", offset_id: int, offset_date: int, add_offset: int, limit: int, max_id: int, min_id: int, hash: int) -> None:
        self.peer = peer  # InputPeer
        self.offset_id = offset_id  # int
        self.offset_date = offset_date  # int
        self.add_offset = add_offset  # int
        self.limit = limit  # int
        self.max_id = max_id  # int
        self.min_id = min_id  # int
        self.hash = hash  # long

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        peer = TLObject.read(data)
        
        offset_id = Int.read(data)
        
        offset_date = Int.read(data)
        
        add_offset = Int.read(data)
        
        limit = Int.read(data)
        
        max_id = Int.read(data)
        
        min_id = Int.read(data)
        
        hash = Long.read(data)
        
        return GetHistory(peer=peer, offset_id=offset_id, offset_date=offset_date, add_offset=add_offset, limit=limit, max_id=max_id, min_id=min_id, hash=hash)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.peer.write())
        
        data.write(Int(self.offset_id))
        
        data.write(Int(self.offset_date))
        
        data.write(Int(self.add_offset))
        
        data.write(Int(self.limit))
        
        data.write(Int(self.max_id))
        
        data.write(Int(self.min_id))
        
        data.write(Long(self.hash))
        
        return data.getvalue()

from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class GetUnreadMentions(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x46578472``

    Parameters:
        peer: :obj:`InputPeer <pyeitaa.raw.base.InputPeer>`
        offset_id: ``int`` ``32-bit``
        add_offset: ``int`` ``32-bit``
        limit: ``int`` ``32-bit``
        max_id: ``int`` ``32-bit``
        min_id: ``int`` ``32-bit``

    Returns:
        :obj:`messages.Messages <pyeitaa.raw.base.messages.Messages>`
    """

    __slots__: List[str] = ["peer", "offset_id", "add_offset", "limit", "max_id", "min_id"]

    ID = 0x46578472
    QUALNAME = "functions.messages.GetUnreadMentions"

    def __init__(self, *, peer: "raw.base.InputPeer", offset_id: int, add_offset: int, limit: int, max_id: int, min_id: int) -> None:
        self.peer = peer  # InputPeer
        self.offset_id = offset_id  # int
        self.add_offset = add_offset  # int
        self.limit = limit  # int
        self.max_id = max_id  # int
        self.min_id = min_id  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        peer = TLObject.read(data)
        
        offset_id = Int.read(data)
        
        add_offset = Int.read(data)
        
        limit = Int.read(data)
        
        max_id = Int.read(data)
        
        min_id = Int.read(data)
        
        return GetUnreadMentions(peer=peer, offset_id=offset_id, add_offset=add_offset, limit=limit, max_id=max_id, min_id=min_id)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.peer.write())
        
        data.write(Int(self.offset_id))
        
        data.write(Int(self.add_offset))
        
        data.write(Int(self.limit))
        
        data.write(Int(self.max_id))
        
        data.write(Int(self.min_id))
        
        return data.getvalue()

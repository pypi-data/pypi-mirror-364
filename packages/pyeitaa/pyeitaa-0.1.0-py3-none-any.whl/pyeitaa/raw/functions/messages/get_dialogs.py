from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class GetDialogs(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x5f0b34b1``

    Parameters:
        offset_date: ``int`` ``32-bit``
        offset_id: ``int`` ``32-bit``
        offset_peer: :obj:`InputPeer <pyeitaa.raw.base.InputPeer>`
        limit: ``int`` ``32-bit``
        hash: ``int`` ``64-bit``
        exclude_pinned (optional): ``bool``
        folder_id (optional): ``int`` ``32-bit``

    Returns:
        :obj:`messages.Dialogs <pyeitaa.raw.base.messages.Dialogs>`
    """

    __slots__: List[str] = ["offset_date", "offset_id", "offset_peer", "limit", "hash", "exclude_pinned", "folder_id"]

    ID = -0x5f0b34b1
    QUALNAME = "functions.messages.GetDialogs"

    def __init__(self, *, offset_date: int, offset_id: int, offset_peer: "raw.base.InputPeer", limit: int, hash: int, exclude_pinned: Optional[bool] = None, folder_id: Optional[int] = None) -> None:
        self.offset_date = offset_date  # int
        self.offset_id = offset_id  # int
        self.offset_peer = offset_peer  # InputPeer
        self.limit = limit  # int
        self.hash = hash  # long
        self.exclude_pinned = exclude_pinned  # flags.0?true
        self.folder_id = folder_id  # flags.1?int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        exclude_pinned = True if flags & (1 << 0) else False
        folder_id = Int.read(data) if flags & (1 << 1) else None
        offset_date = Int.read(data)
        
        offset_id = Int.read(data)
        
        offset_peer = TLObject.read(data)
        
        limit = Int.read(data)
        
        hash = Long.read(data)
        
        return GetDialogs(offset_date=offset_date, offset_id=offset_id, offset_peer=offset_peer, limit=limit, hash=hash, exclude_pinned=exclude_pinned, folder_id=folder_id)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.exclude_pinned else 0
        flags |= (1 << 1) if self.folder_id is not None else 0
        data.write(Int(flags))
        
        if self.folder_id is not None:
            data.write(Int(self.folder_id))
        
        data.write(Int(self.offset_date))
        
        data.write(Int(self.offset_id))
        
        data.write(self.offset_peer.write())
        
        data.write(Int(self.limit))
        
        data.write(Long(self.hash))
        
        return data.getvalue()

from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class UpdateReadHistoryInbox(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.Update`.

    Details:
        - Layer: ``135``
        - ID: ``-0x6368b021``

    Parameters:
        peer: :obj:`Peer <pyeitaa.raw.base.Peer>`
        max_id: ``int`` ``32-bit``
        still_unread_count: ``int`` ``32-bit``
        pts: ``int`` ``32-bit``
        pts_count: ``int`` ``32-bit``
        folder_id (optional): ``int`` ``32-bit``
    """

    __slots__: List[str] = ["peer", "max_id", "still_unread_count", "pts", "pts_count", "folder_id"]

    ID = -0x6368b021
    QUALNAME = "types.UpdateReadHistoryInbox"

    def __init__(self, *, peer: "raw.base.Peer", max_id: int, still_unread_count: int, pts: int, pts_count: int, folder_id: Optional[int] = None) -> None:
        self.peer = peer  # Peer
        self.max_id = max_id  # int
        self.still_unread_count = still_unread_count  # int
        self.pts = pts  # int
        self.pts_count = pts_count  # int
        self.folder_id = folder_id  # flags.0?int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        folder_id = Int.read(data) if flags & (1 << 0) else None
        peer = TLObject.read(data)
        
        max_id = Int.read(data)
        
        still_unread_count = Int.read(data)
        
        pts = Int.read(data)
        
        pts_count = Int.read(data)
        
        return UpdateReadHistoryInbox(peer=peer, max_id=max_id, still_unread_count=still_unread_count, pts=pts, pts_count=pts_count, folder_id=folder_id)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.folder_id is not None else 0
        data.write(Int(flags))
        
        if self.folder_id is not None:
            data.write(Int(self.folder_id))
        
        data.write(self.peer.write())
        
        data.write(Int(self.max_id))
        
        data.write(Int(self.still_unread_count))
        
        data.write(Int(self.pts))
        
        data.write(Int(self.pts_count))
        
        return data.getvalue()

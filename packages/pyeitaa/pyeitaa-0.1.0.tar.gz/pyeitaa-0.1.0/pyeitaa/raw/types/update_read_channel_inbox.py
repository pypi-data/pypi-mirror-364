from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long
from pyeitaa.raw.core import TLObject
from typing import List, Optional, Any, Self


class UpdateReadChannelInbox(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.Update`.

    Details:
        - Layer: ``135``
        - ID: ``-0x6dd191f0``

    Parameters:
        channel_id: ``int`` ``64-bit``
        max_id: ``int`` ``32-bit``
        still_unread_count: ``int`` ``32-bit``
        pts: ``int`` ``32-bit``
        folder_id (optional): ``int`` ``32-bit``
    """

    __slots__: List[str] = ["channel_id", "max_id", "still_unread_count", "pts", "folder_id"]

    ID = -0x6dd191f0
    QUALNAME = "types.UpdateReadChannelInbox"

    def __init__(self, *, channel_id: int, max_id: int, still_unread_count: int, pts: int, folder_id: Optional[int] = None) -> None:
        self.channel_id = channel_id  # long
        self.max_id = max_id  # int
        self.still_unread_count = still_unread_count  # int
        self.pts = pts  # int
        self.folder_id = folder_id  # flags.0?int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        folder_id = Int.read(data) if flags & (1 << 0) else None
        channel_id = Long.read(data)
        
        max_id = Int.read(data)
        
        still_unread_count = Int.read(data)
        
        pts = Int.read(data)
        
        return UpdateReadChannelInbox(channel_id=channel_id, max_id=max_id, still_unread_count=still_unread_count, pts=pts, folder_id=folder_id)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.folder_id is not None else 0
        data.write(Int(flags))
        
        if self.folder_id is not None:
            data.write(Int(self.folder_id))
        
        data.write(Long(self.channel_id))
        
        data.write(Int(self.max_id))
        
        data.write(Int(self.still_unread_count))
        
        data.write(Int(self.pts))
        
        return data.getvalue()

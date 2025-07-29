from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class UpdateFolderPeers(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.Update`.

    Details:
        - Layer: ``135``
        - ID: ``0x19360dc0``

    Parameters:
        folder_peers: List of :obj:`FolderPeer <pyeitaa.raw.base.FolderPeer>`
        pts: ``int`` ``32-bit``
        pts_count: ``int`` ``32-bit``
    """

    __slots__: List[str] = ["folder_peers", "pts", "pts_count"]

    ID = 0x19360dc0
    QUALNAME = "types.UpdateFolderPeers"

    def __init__(self, *, folder_peers: List["raw.base.FolderPeer"], pts: int, pts_count: int) -> None:
        self.folder_peers = folder_peers  # Vector<FolderPeer>
        self.pts = pts  # int
        self.pts_count = pts_count  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        folder_peers = TLObject.read(data)
        
        pts = Int.read(data)
        
        pts_count = Int.read(data)
        
        return UpdateFolderPeers(folder_peers=folder_peers, pts=pts, pts_count=pts_count)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Vector(self.folder_peers))
        
        data.write(Int(self.pts))
        
        data.write(Int(self.pts_count))
        
        return data.getvalue()

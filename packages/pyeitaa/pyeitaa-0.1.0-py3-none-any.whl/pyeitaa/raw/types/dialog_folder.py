from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class DialogFolder(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.Dialog`.

    Details:
        - Layer: ``135``
        - ID: ``0x71bd134c``

    Parameters:
        folder: :obj:`Folder <pyeitaa.raw.base.Folder>`
        peer: :obj:`Peer <pyeitaa.raw.base.Peer>`
        top_message: ``int`` ``32-bit``
        unread_muted_peers_count: ``int`` ``32-bit``
        unread_unmuted_peers_count: ``int`` ``32-bit``
        unread_muted_messages_count: ``int`` ``32-bit``
        unread_unmuted_messages_count: ``int`` ``32-bit``
        pinned (optional): ``bool``
    """

    __slots__: List[str] = ["folder", "peer", "top_message", "unread_muted_peers_count", "unread_unmuted_peers_count", "unread_muted_messages_count", "unread_unmuted_messages_count", "pinned"]

    ID = 0x71bd134c
    QUALNAME = "types.DialogFolder"

    def __init__(self, *, folder: "raw.base.Folder", peer: "raw.base.Peer", top_message: int, unread_muted_peers_count: int, unread_unmuted_peers_count: int, unread_muted_messages_count: int, unread_unmuted_messages_count: int, pinned: Optional[bool] = None) -> None:
        self.folder = folder  # Folder
        self.peer = peer  # Peer
        self.top_message = top_message  # int
        self.unread_muted_peers_count = unread_muted_peers_count  # int
        self.unread_unmuted_peers_count = unread_unmuted_peers_count  # int
        self.unread_muted_messages_count = unread_muted_messages_count  # int
        self.unread_unmuted_messages_count = unread_unmuted_messages_count  # int
        self.pinned = pinned  # flags.2?true

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        pinned = True if flags & (1 << 2) else False
        folder = TLObject.read(data)
        
        peer = TLObject.read(data)
        
        top_message = Int.read(data)
        
        unread_muted_peers_count = Int.read(data)
        
        unread_unmuted_peers_count = Int.read(data)
        
        unread_muted_messages_count = Int.read(data)
        
        unread_unmuted_messages_count = Int.read(data)
        
        return DialogFolder(folder=folder, peer=peer, top_message=top_message, unread_muted_peers_count=unread_muted_peers_count, unread_unmuted_peers_count=unread_unmuted_peers_count, unread_muted_messages_count=unread_muted_messages_count, unread_unmuted_messages_count=unread_unmuted_messages_count, pinned=pinned)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 2) if self.pinned else 0
        data.write(Int(flags))
        
        data.write(self.folder.write())
        
        data.write(self.peer.write())
        
        data.write(Int(self.top_message))
        
        data.write(Int(self.unread_muted_peers_count))
        
        data.write(Int(self.unread_unmuted_peers_count))
        
        data.write(Int(self.unread_muted_messages_count))
        
        data.write(Int(self.unread_unmuted_messages_count))
        
        return data.getvalue()

from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class ChannelParticipantBanned(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.ChannelParticipant`.

    Details:
        - Layer: ``135``
        - ID: ``0x6df8014e``

    Parameters:
        peer: :obj:`Peer <pyeitaa.raw.base.Peer>`
        kicked_by: ``int`` ``64-bit``
        date: ``int`` ``32-bit``
        banned_rights: :obj:`ChatBannedRights <pyeitaa.raw.base.ChatBannedRights>`
        left (optional): ``bool``
    """

    __slots__: List[str] = ["peer", "kicked_by", "date", "banned_rights", "left"]

    ID = 0x6df8014e
    QUALNAME = "types.ChannelParticipantBanned"

    def __init__(self, *, peer: "raw.base.Peer", kicked_by: int, date: int, banned_rights: "raw.base.ChatBannedRights", left: Optional[bool] = None) -> None:
        self.peer = peer  # Peer
        self.kicked_by = kicked_by  # long
        self.date = date  # int
        self.banned_rights = banned_rights  # ChatBannedRights
        self.left = left  # flags.0?true

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        left = True if flags & (1 << 0) else False
        peer = TLObject.read(data)
        
        kicked_by = Long.read(data)
        
        date = Int.read(data)
        
        banned_rights = TLObject.read(data)
        
        return ChannelParticipantBanned(peer=peer, kicked_by=kicked_by, date=date, banned_rights=banned_rights, left=left)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.left else 0
        data.write(Int(flags))
        
        data.write(self.peer.write())
        
        data.write(Long(self.kicked_by))
        
        data.write(Int(self.date))
        
        data.write(self.banned_rights.write())
        
        return data.getvalue()

from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class UpdateChatDefaultBannedRights(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.Update`.

    Details:
        - Layer: ``135``
        - ID: ``0x54c01850``

    Parameters:
        peer: :obj:`Peer <pyeitaa.raw.base.Peer>`
        default_banned_rights: :obj:`ChatBannedRights <pyeitaa.raw.base.ChatBannedRights>`
        version: ``int`` ``32-bit``
    """

    __slots__: List[str] = ["peer", "default_banned_rights", "version"]

    ID = 0x54c01850
    QUALNAME = "types.UpdateChatDefaultBannedRights"

    def __init__(self, *, peer: "raw.base.Peer", default_banned_rights: "raw.base.ChatBannedRights", version: int) -> None:
        self.peer = peer  # Peer
        self.default_banned_rights = default_banned_rights  # ChatBannedRights
        self.version = version  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        peer = TLObject.read(data)
        
        default_banned_rights = TLObject.read(data)
        
        version = Int.read(data)
        
        return UpdateChatDefaultBannedRights(peer=peer, default_banned_rights=default_banned_rights, version=version)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.peer.write())
        
        data.write(self.default_banned_rights.write())
        
        data.write(Int(self.version))
        
        return data.getvalue()

from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class EditChatDefaultBannedRights(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x5a7994bf``

    Parameters:
        peer: :obj:`InputPeer <pyeitaa.raw.base.InputPeer>`
        banned_rights: :obj:`ChatBannedRights <pyeitaa.raw.base.ChatBannedRights>`

    Returns:
        :obj:`Updates <pyeitaa.raw.base.Updates>`
    """

    __slots__: List[str] = ["peer", "banned_rights"]

    ID = -0x5a7994bf
    QUALNAME = "functions.messages.EditChatDefaultBannedRights"

    def __init__(self, *, peer: "raw.base.InputPeer", banned_rights: "raw.base.ChatBannedRights") -> None:
        self.peer = peer  # InputPeer
        self.banned_rights = banned_rights  # ChatBannedRights

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        peer = TLObject.read(data)
        
        banned_rights = TLObject.read(data)
        
        return EditChatDefaultBannedRights(peer=peer, banned_rights=banned_rights)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.peer.write())
        
        data.write(self.banned_rights.write())
        
        return data.getvalue()

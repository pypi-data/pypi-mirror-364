from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class DeleteRevokedExportedChatInvites(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x56987bd5``

    Parameters:
        peer: :obj:`InputPeer <pyeitaa.raw.base.InputPeer>`
        admin_id: :obj:`InputUser <pyeitaa.raw.base.InputUser>`

    Returns:
        ``bool``
    """

    __slots__: List[str] = ["peer", "admin_id"]

    ID = 0x56987bd5
    QUALNAME = "functions.messages.DeleteRevokedExportedChatInvites"

    def __init__(self, *, peer: "raw.base.InputPeer", admin_id: "raw.base.InputUser") -> None:
        self.peer = peer  # InputPeer
        self.admin_id = admin_id  # InputUser

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        peer = TLObject.read(data)
        
        admin_id = TLObject.read(data)
        
        return DeleteRevokedExportedChatInvites(peer=peer, admin_id=admin_id)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.peer.write())
        
        data.write(self.admin_id.write())
        
        return data.getvalue()

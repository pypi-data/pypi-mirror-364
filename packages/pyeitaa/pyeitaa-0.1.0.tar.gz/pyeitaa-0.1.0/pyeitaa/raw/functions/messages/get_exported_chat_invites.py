from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class GetExportedChatInvites(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x5d4a5c0a``

    Parameters:
        peer: :obj:`InputPeer <pyeitaa.raw.base.InputPeer>`
        admin_id: :obj:`InputUser <pyeitaa.raw.base.InputUser>`
        limit: ``int`` ``32-bit``
        revoked (optional): ``bool``
        offset_date (optional): ``int`` ``32-bit``
        offset_link (optional): ``str``

    Returns:
        :obj:`messages.ExportedChatInvites <pyeitaa.raw.base.messages.ExportedChatInvites>`
    """

    __slots__: List[str] = ["peer", "admin_id", "limit", "revoked", "offset_date", "offset_link"]

    ID = -0x5d4a5c0a
    QUALNAME = "functions.messages.GetExportedChatInvites"

    def __init__(self, *, peer: "raw.base.InputPeer", admin_id: "raw.base.InputUser", limit: int, revoked: Optional[bool] = None, offset_date: Optional[int] = None, offset_link: Optional[str] = None) -> None:
        self.peer = peer  # InputPeer
        self.admin_id = admin_id  # InputUser
        self.limit = limit  # int
        self.revoked = revoked  # flags.3?true
        self.offset_date = offset_date  # flags.2?int
        self.offset_link = offset_link  # flags.2?string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        revoked = True if flags & (1 << 3) else False
        peer = TLObject.read(data)
        
        admin_id = TLObject.read(data)
        
        offset_date = Int.read(data) if flags & (1 << 2) else None
        offset_link = String.read(data) if flags & (1 << 2) else None
        limit = Int.read(data)
        
        return GetExportedChatInvites(peer=peer, admin_id=admin_id, limit=limit, revoked=revoked, offset_date=offset_date, offset_link=offset_link)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 3) if self.revoked else 0
        flags |= (1 << 2) if self.offset_date is not None else 0
        flags |= (1 << 2) if self.offset_link is not None else 0
        data.write(Int(flags))
        
        data.write(self.peer.write())
        
        data.write(self.admin_id.write())
        
        if self.offset_date is not None:
            data.write(Int(self.offset_date))
        
        if self.offset_link is not None:
            data.write(String(self.offset_link))
        
        data.write(Int(self.limit))
        
        return data.getvalue()

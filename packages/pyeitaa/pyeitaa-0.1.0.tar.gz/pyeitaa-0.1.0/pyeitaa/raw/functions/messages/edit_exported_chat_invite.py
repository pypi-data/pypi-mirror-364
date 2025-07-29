from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class EditExportedChatInvite(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x2e4ffbe``

    Parameters:
        peer: :obj:`InputPeer <pyeitaa.raw.base.InputPeer>`
        link: ``str``
        revoked (optional): ``bool``
        expire_date (optional): ``int`` ``32-bit``
        usage_limit (optional): ``int`` ``32-bit``

    Returns:
        :obj:`messages.ExportedChatInvite <pyeitaa.raw.base.messages.ExportedChatInvite>`
    """

    __slots__: List[str] = ["peer", "link", "revoked", "expire_date", "usage_limit"]

    ID = 0x2e4ffbe
    QUALNAME = "functions.messages.EditExportedChatInvite"

    def __init__(self, *, peer: "raw.base.InputPeer", link: str, revoked: Optional[bool] = None, expire_date: Optional[int] = None, usage_limit: Optional[int] = None) -> None:
        self.peer = peer  # InputPeer
        self.link = link  # string
        self.revoked = revoked  # flags.2?true
        self.expire_date = expire_date  # flags.0?int
        self.usage_limit = usage_limit  # flags.1?int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        revoked = True if flags & (1 << 2) else False
        peer = TLObject.read(data)
        
        link = String.read(data)
        
        expire_date = Int.read(data) if flags & (1 << 0) else None
        usage_limit = Int.read(data) if flags & (1 << 1) else None
        return EditExportedChatInvite(peer=peer, link=link, revoked=revoked, expire_date=expire_date, usage_limit=usage_limit)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 2) if self.revoked else 0
        flags |= (1 << 0) if self.expire_date is not None else 0
        flags |= (1 << 1) if self.usage_limit is not None else 0
        data.write(Int(flags))
        
        data.write(self.peer.write())
        
        data.write(String(self.link))
        
        if self.expire_date is not None:
            data.write(Int(self.expire_date))
        
        if self.usage_limit is not None:
            data.write(Int(self.usage_limit))
        
        return data.getvalue()

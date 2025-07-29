from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class ExportChatInvite(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x14b9bcd7``

    Parameters:
        peer: :obj:`InputPeer <pyeitaa.raw.base.InputPeer>`
        legacy_revoke_permanent (optional): ``bool``
        expire_date (optional): ``int`` ``32-bit``
        usage_limit (optional): ``int`` ``32-bit``

    Returns:
        :obj:`ExportedChatInvite <pyeitaa.raw.base.ExportedChatInvite>`
    """

    __slots__: List[str] = ["peer", "legacy_revoke_permanent", "expire_date", "usage_limit"]

    ID = 0x14b9bcd7
    QUALNAME = "functions.messages.ExportChatInvite"

    def __init__(self, *, peer: "raw.base.InputPeer", legacy_revoke_permanent: Optional[bool] = None, expire_date: Optional[int] = None, usage_limit: Optional[int] = None) -> None:
        self.peer = peer  # InputPeer
        self.legacy_revoke_permanent = legacy_revoke_permanent  # flags.2?true
        self.expire_date = expire_date  # flags.0?int
        self.usage_limit = usage_limit  # flags.1?int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        legacy_revoke_permanent = True if flags & (1 << 2) else False
        peer = TLObject.read(data)
        
        expire_date = Int.read(data) if flags & (1 << 0) else None
        usage_limit = Int.read(data) if flags & (1 << 1) else None
        return ExportChatInvite(peer=peer, legacy_revoke_permanent=legacy_revoke_permanent, expire_date=expire_date, usage_limit=usage_limit)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 2) if self.legacy_revoke_permanent else 0
        flags |= (1 << 0) if self.expire_date is not None else 0
        flags |= (1 << 1) if self.usage_limit is not None else 0
        data.write(Int(flags))
        
        data.write(self.peer.write())
        
        if self.expire_date is not None:
            data.write(Int(self.expire_date))
        
        if self.usage_limit is not None:
            data.write(Int(self.usage_limit))
        
        return data.getvalue()

from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, String
from pyeitaa.raw.core import TLObject
from typing import List, Optional, Any, Self


class ChatInviteExported(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.ExportedChatInvite`.

    Details:
        - Layer: ``135``
        - ID: ``-0x4e7efa18``

    Parameters:
        link: ``str``
        admin_id: ``int`` ``64-bit``
        date: ``int`` ``32-bit``
        revoked (optional): ``bool``
        permanent (optional): ``bool``
        start_date (optional): ``int`` ``32-bit``
        expire_date (optional): ``int`` ``32-bit``
        usage_limit (optional): ``int`` ``32-bit``
        usage (optional): ``int`` ``32-bit``

    See Also:
        This object can be returned by 2 methods:

        .. hlist::
            :columns: 2

            - :obj:`messages.ExportChatInvite <pyeitaa.raw.functions.messages.ExportChatInvite>`
            - :obj:`messages.ExportChatInviteLayer84 <pyeitaa.raw.functions.messages.ExportChatInviteLayer84>`
    """

    __slots__: List[str] = ["link", "admin_id", "date", "revoked", "permanent", "start_date", "expire_date", "usage_limit", "usage"]

    ID = -0x4e7efa18
    QUALNAME = "types.ChatInviteExported"

    def __init__(self, *, link: str, admin_id: int, date: int, revoked: Optional[bool] = None, permanent: Optional[bool] = None, start_date: Optional[int] = None, expire_date: Optional[int] = None, usage_limit: Optional[int] = None, usage: Optional[int] = None) -> None:
        self.link = link  # string
        self.admin_id = admin_id  # long
        self.date = date  # int
        self.revoked = revoked  # flags.0?true
        self.permanent = permanent  # flags.5?true
        self.start_date = start_date  # flags.4?int
        self.expire_date = expire_date  # flags.1?int
        self.usage_limit = usage_limit  # flags.2?int
        self.usage = usage  # flags.3?int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        revoked = True if flags & (1 << 0) else False
        permanent = True if flags & (1 << 5) else False
        link = String.read(data)
        
        admin_id = Long.read(data)
        
        date = Int.read(data)
        
        start_date = Int.read(data) if flags & (1 << 4) else None
        expire_date = Int.read(data) if flags & (1 << 1) else None
        usage_limit = Int.read(data) if flags & (1 << 2) else None
        usage = Int.read(data) if flags & (1 << 3) else None
        return ChatInviteExported(link=link, admin_id=admin_id, date=date, revoked=revoked, permanent=permanent, start_date=start_date, expire_date=expire_date, usage_limit=usage_limit, usage=usage)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.revoked else 0
        flags |= (1 << 5) if self.permanent else 0
        flags |= (1 << 4) if self.start_date is not None else 0
        flags |= (1 << 1) if self.expire_date is not None else 0
        flags |= (1 << 2) if self.usage_limit is not None else 0
        flags |= (1 << 3) if self.usage is not None else 0
        data.write(Int(flags))
        
        data.write(String(self.link))
        
        data.write(Long(self.admin_id))
        
        data.write(Int(self.date))
        
        if self.start_date is not None:
            data.write(Int(self.start_date))
        
        if self.expire_date is not None:
            data.write(Int(self.expire_date))
        
        if self.usage_limit is not None:
            data.write(Int(self.usage_limit))
        
        if self.usage is not None:
            data.write(Int(self.usage))
        
        return data.getvalue()

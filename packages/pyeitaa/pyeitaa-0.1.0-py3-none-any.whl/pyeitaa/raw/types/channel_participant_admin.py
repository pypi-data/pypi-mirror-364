from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, String
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class ChannelParticipantAdmin(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.ChannelParticipant`.

    Details:
        - Layer: ``135``
        - ID: ``0x34c3bb53``

    Parameters:
        user_id: ``int`` ``64-bit``
        promoted_by: ``int`` ``64-bit``
        date: ``int`` ``32-bit``
        admin_rights: :obj:`ChatAdminRights <pyeitaa.raw.base.ChatAdminRights>`
        can_edit (optional): ``bool``
        is_self (optional): ``bool``
        inviter_id (optional): ``int`` ``64-bit``
        rank (optional): ``str``
    """

    __slots__: List[str] = ["user_id", "promoted_by", "date", "admin_rights", "can_edit", "is_self", "inviter_id", "rank"]

    ID = 0x34c3bb53
    QUALNAME = "types.ChannelParticipantAdmin"

    def __init__(self, *, user_id: int, promoted_by: int, date: int, admin_rights: "raw.base.ChatAdminRights", can_edit: Optional[bool] = None, is_self: Optional[bool] = None, inviter_id: Optional[int] = None, rank: Optional[str] = None) -> None:
        self.user_id = user_id  # long
        self.promoted_by = promoted_by  # long
        self.date = date  # int
        self.admin_rights = admin_rights  # ChatAdminRights
        self.can_edit = can_edit  # flags.0?true
        self.is_self = is_self  # flags.1?true
        self.inviter_id = inviter_id  # flags.1?long
        self.rank = rank  # flags.2?string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        can_edit = True if flags & (1 << 0) else False
        is_self = True if flags & (1 << 1) else False
        user_id = Long.read(data)
        
        inviter_id = Long.read(data) if flags & (1 << 1) else None
        promoted_by = Long.read(data)
        
        date = Int.read(data)
        
        admin_rights = TLObject.read(data)
        
        rank = String.read(data) if flags & (1 << 2) else None
        return ChannelParticipantAdmin(user_id=user_id, promoted_by=promoted_by, date=date, admin_rights=admin_rights, can_edit=can_edit, is_self=is_self, inviter_id=inviter_id, rank=rank)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.can_edit else 0
        flags |= (1 << 1) if self.is_self else 0
        flags |= (1 << 1) if self.inviter_id is not None else 0
        flags |= (1 << 2) if self.rank is not None else 0
        data.write(Int(flags))
        
        data.write(Long(self.user_id))
        
        if self.inviter_id is not None:
            data.write(Long(self.inviter_id))
        
        data.write(Long(self.promoted_by))
        
        data.write(Int(self.date))
        
        data.write(self.admin_rights.write())
        
        if self.rank is not None:
            data.write(String(self.rank))
        
        return data.getvalue()

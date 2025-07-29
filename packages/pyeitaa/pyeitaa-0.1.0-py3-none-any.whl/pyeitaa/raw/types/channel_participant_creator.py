from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, String
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class ChannelParticipantCreator(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.ChannelParticipant`.

    Details:
        - Layer: ``135``
        - ID: ``0x2fe601d3``

    Parameters:
        user_id: ``int`` ``64-bit``
        admin_rights: :obj:`ChatAdminRights <pyeitaa.raw.base.ChatAdminRights>`
        rank (optional): ``str``
    """

    __slots__: List[str] = ["user_id", "admin_rights", "rank"]

    ID = 0x2fe601d3
    QUALNAME = "types.ChannelParticipantCreator"

    def __init__(self, *, user_id: int, admin_rights: "raw.base.ChatAdminRights", rank: Optional[str] = None) -> None:
        self.user_id = user_id  # long
        self.admin_rights = admin_rights  # ChatAdminRights
        self.rank = rank  # flags.0?string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        user_id = Long.read(data)
        
        admin_rights = TLObject.read(data)
        
        rank = String.read(data) if flags & (1 << 0) else None
        return ChannelParticipantCreator(user_id=user_id, admin_rights=admin_rights, rank=rank)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.rank is not None else 0
        data.write(Int(flags))
        
        data.write(Long(self.user_id))
        
        data.write(self.admin_rights.write())
        
        if self.rank is not None:
            data.write(String(self.rank))
        
        return data.getvalue()

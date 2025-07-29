from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class ChannelAdminLogEventActionDefaultBannedRights(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.ChannelAdminLogEventAction`.

    Details:
        - Layer: ``135``
        - ID: ``0x2df5fc0a``

    Parameters:
        prev_banned_rights: :obj:`ChatBannedRights <pyeitaa.raw.base.ChatBannedRights>`
        new_banned_rights: :obj:`ChatBannedRights <pyeitaa.raw.base.ChatBannedRights>`
    """

    __slots__: List[str] = ["prev_banned_rights", "new_banned_rights"]

    ID = 0x2df5fc0a
    QUALNAME = "types.ChannelAdminLogEventActionDefaultBannedRights"

    def __init__(self, *, prev_banned_rights: "raw.base.ChatBannedRights", new_banned_rights: "raw.base.ChatBannedRights") -> None:
        self.prev_banned_rights = prev_banned_rights  # ChatBannedRights
        self.new_banned_rights = new_banned_rights  # ChatBannedRights

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        prev_banned_rights = TLObject.read(data)
        
        new_banned_rights = TLObject.read(data)
        
        return ChannelAdminLogEventActionDefaultBannedRights(prev_banned_rights=prev_banned_rights, new_banned_rights=new_banned_rights)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.prev_banned_rights.write())
        
        data.write(self.new_banned_rights.write())
        
        return data.getvalue()

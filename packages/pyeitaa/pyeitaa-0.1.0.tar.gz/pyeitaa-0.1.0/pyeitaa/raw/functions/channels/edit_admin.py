from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class EditAdmin(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x2cc376fe``

    Parameters:
        channel: :obj:`InputChannel <pyeitaa.raw.base.InputChannel>`
        user_id: :obj:`InputUser <pyeitaa.raw.base.InputUser>`
        admin_rights: :obj:`ChatAdminRights <pyeitaa.raw.base.ChatAdminRights>`
        rank: ``str``

    Returns:
        :obj:`Updates <pyeitaa.raw.base.Updates>`
    """

    __slots__: List[str] = ["channel", "user_id", "admin_rights", "rank"]

    ID = -0x2cc376fe
    QUALNAME = "functions.channels.EditAdmin"

    def __init__(self, *, channel: "raw.base.InputChannel", user_id: "raw.base.InputUser", admin_rights: "raw.base.ChatAdminRights", rank: str) -> None:
        self.channel = channel  # InputChannel
        self.user_id = user_id  # InputUser
        self.admin_rights = admin_rights  # ChatAdminRights
        self.rank = rank  # string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        channel = TLObject.read(data)
        
        user_id = TLObject.read(data)
        
        admin_rights = TLObject.read(data)
        
        rank = String.read(data)
        
        return EditAdmin(channel=channel, user_id=user_id, admin_rights=admin_rights, rank=rank)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.channel.write())
        
        data.write(self.user_id.write())
        
        data.write(self.admin_rights.write())
        
        data.write(String(self.rank))
        
        return data.getvalue()

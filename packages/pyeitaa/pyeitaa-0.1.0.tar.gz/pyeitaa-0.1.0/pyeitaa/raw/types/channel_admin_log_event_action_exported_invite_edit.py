from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class ChannelAdminLogEventActionExportedInviteEdit(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.ChannelAdminLogEventAction`.

    Details:
        - Layer: ``135``
        - ID: ``-0x16f144a7``

    Parameters:
        prev_invite: :obj:`ExportedChatInvite <pyeitaa.raw.base.ExportedChatInvite>`
        new_invite: :obj:`ExportedChatInvite <pyeitaa.raw.base.ExportedChatInvite>`
    """

    __slots__: List[str] = ["prev_invite", "new_invite"]

    ID = -0x16f144a7
    QUALNAME = "types.ChannelAdminLogEventActionExportedInviteEdit"

    def __init__(self, *, prev_invite: "raw.base.ExportedChatInvite", new_invite: "raw.base.ExportedChatInvite") -> None:
        self.prev_invite = prev_invite  # ExportedChatInvite
        self.new_invite = new_invite  # ExportedChatInvite

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        prev_invite = TLObject.read(data)
        
        new_invite = TLObject.read(data)
        
        return ChannelAdminLogEventActionExportedInviteEdit(prev_invite=prev_invite, new_invite=new_invite)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.prev_invite.write())
        
        data.write(self.new_invite.write())
        
        return data.getvalue()

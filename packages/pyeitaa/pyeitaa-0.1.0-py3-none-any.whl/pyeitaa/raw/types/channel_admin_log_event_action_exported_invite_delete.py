from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class ChannelAdminLogEventActionExportedInviteDelete(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.ChannelAdminLogEventAction`.

    Details:
        - Layer: ``135``
        - ID: ``0x5a50fca4``

    Parameters:
        invite: :obj:`ExportedChatInvite <pyeitaa.raw.base.ExportedChatInvite>`
    """

    __slots__: List[str] = ["invite"]

    ID = 0x5a50fca4
    QUALNAME = "types.ChannelAdminLogEventActionExportedInviteDelete"

    def __init__(self, *, invite: "raw.base.ExportedChatInvite") -> None:
        self.invite = invite  # ExportedChatInvite

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        invite = TLObject.read(data)
        
        return ChannelAdminLogEventActionExportedInviteDelete(invite=invite)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.invite.write())
        
        return data.getvalue()

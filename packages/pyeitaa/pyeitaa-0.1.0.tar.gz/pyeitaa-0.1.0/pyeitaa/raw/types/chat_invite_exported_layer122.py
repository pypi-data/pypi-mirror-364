from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class ChatInviteExportedLayer122(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.ExportedChatInvite`.

    Details:
        - Layer: ``135``
        - ID: ``-0x3d1fa44``

    Parameters:
        link: ``str``

    See Also:
        This object can be returned by 2 methods:

        .. hlist::
            :columns: 2

            - :obj:`messages.ExportChatInvite <pyeitaa.raw.functions.messages.ExportChatInvite>`
            - :obj:`messages.ExportChatInviteLayer84 <pyeitaa.raw.functions.messages.ExportChatInviteLayer84>`
    """

    __slots__: List[str] = ["link"]

    ID = -0x3d1fa44
    QUALNAME = "types.ChatInviteExportedLayer122"

    def __init__(self, *, link: str) -> None:
        self.link = link  # string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        link = String.read(data)
        
        return ChatInviteExportedLayer122(link=link)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(String(self.link))
        
        return data.getvalue()

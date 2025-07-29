from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class ChatInviteEmptyLayer122(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.ExportedChatInvite`.

    Details:
        - Layer: ``135``
        - ID: ``0x69df3769``

    **No parameters required.**

    See Also:
        This object can be returned by 2 methods:

        .. hlist::
            :columns: 2

            - :obj:`messages.ExportChatInvite <pyeitaa.raw.functions.messages.ExportChatInvite>`
            - :obj:`messages.ExportChatInviteLayer84 <pyeitaa.raw.functions.messages.ExportChatInviteLayer84>`
    """

    __slots__: List[str] = []

    ID = 0x69df3769
    QUALNAME = "types.ChatInviteEmptyLayer122"

    def __init__(self) -> None:
        pass

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        return ChatInviteEmptyLayer122()

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        return data.getvalue()

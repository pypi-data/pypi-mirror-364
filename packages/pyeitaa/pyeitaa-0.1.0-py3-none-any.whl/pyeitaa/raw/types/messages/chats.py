from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class Chats(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.messages.Chats`.

    Details:
        - Layer: ``135``
        - ID: ``0x64ff9fd5``

    Parameters:
        chats: List of :obj:`Chat <pyeitaa.raw.base.Chat>`

    See Also:
        This object can be returned by 7 methods:

        .. hlist::
            :columns: 2

            - :obj:`messages.GetChats <pyeitaa.raw.functions.messages.GetChats>`
            - :obj:`messages.GetCommonChats <pyeitaa.raw.functions.messages.GetCommonChats>`
            - :obj:`messages.GetAllChats <pyeitaa.raw.functions.messages.GetAllChats>`
            - :obj:`channels.GetChannels <pyeitaa.raw.functions.channels.GetChannels>`
            - :obj:`channels.GetAdminedPublicChannels <pyeitaa.raw.functions.channels.GetAdminedPublicChannels>`
            - :obj:`channels.GetLeftChannels <pyeitaa.raw.functions.channels.GetLeftChannels>`
            - :obj:`channels.GetGroupsForDiscussion <pyeitaa.raw.functions.channels.GetGroupsForDiscussion>`
    """

    __slots__: List[str] = ["chats"]

    ID = 0x64ff9fd5
    QUALNAME = "types.messages.Chats"

    def __init__(self, *, chats: List["raw.base.Chat"]) -> None:
        self.chats = chats  # Vector<Chat>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        chats = TLObject.read(data)
        
        return Chats(chats=chats)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Vector(self.chats))
        
        return data.getvalue()

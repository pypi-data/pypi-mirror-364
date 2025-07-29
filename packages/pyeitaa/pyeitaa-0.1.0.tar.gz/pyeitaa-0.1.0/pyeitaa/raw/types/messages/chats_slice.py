from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class ChatsSlice(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.messages.Chats`.

    Details:
        - Layer: ``135``
        - ID: ``-0x6327eebc``

    Parameters:
        count: ``int`` ``32-bit``
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

    __slots__: List[str] = ["count", "chats"]

    ID = -0x6327eebc
    QUALNAME = "types.messages.ChatsSlice"

    def __init__(self, *, count: int, chats: List["raw.base.Chat"]) -> None:
        self.count = count  # int
        self.chats = chats  # Vector<Chat>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        count = Int.read(data)
        
        chats = TLObject.read(data)
        
        return ChatsSlice(count=count, chats=chats)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Int(self.count))
        
        data.write(Vector(self.chats))
        
        return data.getvalue()

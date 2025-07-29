from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class Messages(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.messages.Messages`.

    Details:
        - Layer: ``135``
        - ID: ``-0x738e7179``

    Parameters:
        messages: List of :obj:`Message <pyeitaa.raw.base.Message>`
        chats: List of :obj:`Chat <pyeitaa.raw.base.Chat>`
        users: List of :obj:`User <pyeitaa.raw.base.User>`

    See Also:
        This object can be returned by 12 methods:

        .. hlist::
            :columns: 2

            - :obj:`messages.GetMessages <pyeitaa.raw.functions.messages.GetMessages>`
            - :obj:`messages.GetHistory <pyeitaa.raw.functions.messages.GetHistory>`
            - :obj:`messages.Search <pyeitaa.raw.functions.messages.Search>`
            - :obj:`messages.SearchGlobal <pyeitaa.raw.functions.messages.SearchGlobal>`
            - :obj:`messages.SearchGlobalExt <pyeitaa.raw.functions.messages.SearchGlobalExt>`
            - :obj:`messages.GetUnreadMentions <pyeitaa.raw.functions.messages.GetUnreadMentions>`
            - :obj:`messages.GetRecentLocations <pyeitaa.raw.functions.messages.GetRecentLocations>`
            - :obj:`messages.GetScheduledHistory <pyeitaa.raw.functions.messages.GetScheduledHistory>`
            - :obj:`messages.GetScheduledMessages <pyeitaa.raw.functions.messages.GetScheduledMessages>`
            - :obj:`messages.GetReplies <pyeitaa.raw.functions.messages.GetReplies>`
            - :obj:`channels.GetMessages <pyeitaa.raw.functions.channels.GetMessages>`
            - :obj:`stats.GetMessagePublicForwards <pyeitaa.raw.functions.stats.GetMessagePublicForwards>`
    """

    __slots__: List[str] = ["messages", "chats", "users"]

    ID = -0x738e7179
    QUALNAME = "types.messages.Messages"

    def __init__(self, *, messages: List["raw.base.Message"], chats: List["raw.base.Chat"], users: List["raw.base.User"]) -> None:
        self.messages = messages  # Vector<Message>
        self.chats = chats  # Vector<Chat>
        self.users = users  # Vector<User>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        messages = TLObject.read(data)
        
        chats = TLObject.read(data)
        
        users = TLObject.read(data)
        
        return Messages(messages=messages, chats=chats, users=users)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Vector(self.messages))
        
        data.write(Vector(self.chats))
        
        data.write(Vector(self.users))
        
        return data.getvalue()

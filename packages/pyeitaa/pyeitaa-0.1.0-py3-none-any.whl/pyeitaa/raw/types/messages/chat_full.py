from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class ChatFull(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.messages.ChatFull`.

    Details:
        - Layer: ``135``
        - ID: ``-0x1a282e64``

    Parameters:
        full_chat: :obj:`ChatFull <pyeitaa.raw.base.ChatFull>`
        chats: List of :obj:`Chat <pyeitaa.raw.base.Chat>`
        users: List of :obj:`User <pyeitaa.raw.base.User>`

    See Also:
        This object can be returned by 2 methods:

        .. hlist::
            :columns: 2

            - :obj:`messages.GetFullChat <pyeitaa.raw.functions.messages.GetFullChat>`
            - :obj:`channels.GetFullChannel <pyeitaa.raw.functions.channels.GetFullChannel>`
    """

    __slots__: List[str] = ["full_chat", "chats", "users"]

    ID = -0x1a282e64
    QUALNAME = "types.messages.ChatFull"

    def __init__(self, *, full_chat: "raw.base.ChatFull", chats: List["raw.base.Chat"], users: List["raw.base.User"]) -> None:
        self.full_chat = full_chat  # ChatFull
        self.chats = chats  # Vector<Chat>
        self.users = users  # Vector<User>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        full_chat = TLObject.read(data)
        
        chats = TLObject.read(data)
        
        users = TLObject.read(data)
        
        return ChatFull(full_chat=full_chat, chats=chats, users=users)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.full_chat.write())
        
        data.write(Vector(self.chats))
        
        data.write(Vector(self.users))
        
        return data.getvalue()

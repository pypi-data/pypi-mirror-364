from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class DiscussionMessage(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.messages.DiscussionMessage`.

    Details:
        - Layer: ``135``
        - ID: ``-0x59cbe87e``

    Parameters:
        messages: List of :obj:`Message <pyeitaa.raw.base.Message>`
        unread_count: ``int`` ``32-bit``
        chats: List of :obj:`Chat <pyeitaa.raw.base.Chat>`
        users: List of :obj:`User <pyeitaa.raw.base.User>`
        max_id (optional): ``int`` ``32-bit``
        read_inbox_max_id (optional): ``int`` ``32-bit``
        read_outbox_max_id (optional): ``int`` ``32-bit``

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`messages.GetDiscussionMessage <pyeitaa.raw.functions.messages.GetDiscussionMessage>`
    """

    __slots__: List[str] = ["messages", "unread_count", "chats", "users", "max_id", "read_inbox_max_id", "read_outbox_max_id"]

    ID = -0x59cbe87e
    QUALNAME = "types.messages.DiscussionMessage"

    def __init__(self, *, messages: List["raw.base.Message"], unread_count: int, chats: List["raw.base.Chat"], users: List["raw.base.User"], max_id: Optional[int] = None, read_inbox_max_id: Optional[int] = None, read_outbox_max_id: Optional[int] = None) -> None:
        self.messages = messages  # Vector<Message>
        self.unread_count = unread_count  # int
        self.chats = chats  # Vector<Chat>
        self.users = users  # Vector<User>
        self.max_id = max_id  # flags.0?int
        self.read_inbox_max_id = read_inbox_max_id  # flags.1?int
        self.read_outbox_max_id = read_outbox_max_id  # flags.2?int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        messages = TLObject.read(data)
        
        max_id = Int.read(data) if flags & (1 << 0) else None
        read_inbox_max_id = Int.read(data) if flags & (1 << 1) else None
        read_outbox_max_id = Int.read(data) if flags & (1 << 2) else None
        unread_count = Int.read(data)
        
        chats = TLObject.read(data)
        
        users = TLObject.read(data)
        
        return DiscussionMessage(messages=messages, unread_count=unread_count, chats=chats, users=users, max_id=max_id, read_inbox_max_id=read_inbox_max_id, read_outbox_max_id=read_outbox_max_id)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.max_id is not None else 0
        flags |= (1 << 1) if self.read_inbox_max_id is not None else 0
        flags |= (1 << 2) if self.read_outbox_max_id is not None else 0
        data.write(Int(flags))
        
        data.write(Vector(self.messages))
        
        if self.max_id is not None:
            data.write(Int(self.max_id))
        
        if self.read_inbox_max_id is not None:
            data.write(Int(self.read_inbox_max_id))
        
        if self.read_outbox_max_id is not None:
            data.write(Int(self.read_outbox_max_id))
        
        data.write(Int(self.unread_count))
        
        data.write(Vector(self.chats))
        
        data.write(Vector(self.users))
        
        return data.getvalue()

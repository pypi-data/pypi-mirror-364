from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class MessageViews(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.messages.MessageViews`.

    Details:
        - Layer: ``135``
        - ID: ``-0x493b0abd``

    Parameters:
        views: List of :obj:`MessageViews <pyeitaa.raw.base.MessageViews>`
        chats: List of :obj:`Chat <pyeitaa.raw.base.Chat>`
        users: List of :obj:`User <pyeitaa.raw.base.User>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`messages.GetMessagesViews <pyeitaa.raw.functions.messages.GetMessagesViews>`
    """

    __slots__: List[str] = ["views", "chats", "users"]

    ID = -0x493b0abd
    QUALNAME = "types.messages.MessageViews"

    def __init__(self, *, views: List["raw.base.MessageViews"], chats: List["raw.base.Chat"], users: List["raw.base.User"]) -> None:
        self.views = views  # Vector<MessageViews>
        self.chats = chats  # Vector<Chat>
        self.users = users  # Vector<User>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        views = TLObject.read(data)
        
        chats = TLObject.read(data)
        
        users = TLObject.read(data)
        
        return MessageViews(views=views, chats=chats, users=users)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Vector(self.views))
        
        data.write(Vector(self.chats))
        
        data.write(Vector(self.users))
        
        return data.getvalue()

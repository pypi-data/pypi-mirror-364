from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class AdminLogResults(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.channels.AdminLogResults`.

    Details:
        - Layer: ``135``
        - ID: ``-0x127508b3``

    Parameters:
        events: List of :obj:`ChannelAdminLogEvent <pyeitaa.raw.base.ChannelAdminLogEvent>`
        chats: List of :obj:`Chat <pyeitaa.raw.base.Chat>`
        users: List of :obj:`User <pyeitaa.raw.base.User>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`channels.GetAdminLog <pyeitaa.raw.functions.channels.GetAdminLog>`
    """

    __slots__: List[str] = ["events", "chats", "users"]

    ID = -0x127508b3
    QUALNAME = "types.channels.AdminLogResults"

    def __init__(self, *, events: List["raw.base.ChannelAdminLogEvent"], chats: List["raw.base.Chat"], users: List["raw.base.User"]) -> None:
        self.events = events  # Vector<ChannelAdminLogEvent>
        self.chats = chats  # Vector<Chat>
        self.users = users  # Vector<User>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        events = TLObject.read(data)
        
        chats = TLObject.read(data)
        
        users = TLObject.read(data)
        
        return AdminLogResults(events=events, chats=chats, users=users)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Vector(self.events))
        
        data.write(Vector(self.chats))
        
        data.write(Vector(self.users))
        
        return data.getvalue()

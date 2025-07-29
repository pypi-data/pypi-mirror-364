from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class InactiveChats(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.messages.InactiveChats`.

    Details:
        - Layer: ``135``
        - ID: ``-0x56d8013b``

    Parameters:
        dates: List of ``int`` ``32-bit``
        chats: List of :obj:`Chat <pyeitaa.raw.base.Chat>`
        users: List of :obj:`User <pyeitaa.raw.base.User>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`channels.GetInactiveChannels <pyeitaa.raw.functions.channels.GetInactiveChannels>`
    """

    __slots__: List[str] = ["dates", "chats", "users"]

    ID = -0x56d8013b
    QUALNAME = "types.messages.InactiveChats"

    def __init__(self, *, dates: List[int], chats: List["raw.base.Chat"], users: List["raw.base.User"]) -> None:
        self.dates = dates  # Vector<int>
        self.chats = chats  # Vector<Chat>
        self.users = users  # Vector<User>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        dates = TLObject.read(data, Int)
        
        chats = TLObject.read(data)
        
        users = TLObject.read(data)
        
        return InactiveChats(dates=dates, chats=chats, users=users)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Vector(self.dates, Int))
        
        data.write(Vector(self.chats))
        
        data.write(Vector(self.users))
        
        return data.getvalue()

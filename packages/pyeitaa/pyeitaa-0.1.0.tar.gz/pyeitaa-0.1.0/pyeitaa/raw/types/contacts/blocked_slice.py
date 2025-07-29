from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class BlockedSlice(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.contacts.Blocked`.

    Details:
        - Layer: ``135``
        - ID: ``-0x1e99be6c``

    Parameters:
        count: ``int`` ``32-bit``
        blocked: List of :obj:`PeerBlocked <pyeitaa.raw.base.PeerBlocked>`
        chats: List of :obj:`Chat <pyeitaa.raw.base.Chat>`
        users: List of :obj:`User <pyeitaa.raw.base.User>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`contacts.GetBlocked <pyeitaa.raw.functions.contacts.GetBlocked>`
    """

    __slots__: List[str] = ["count", "blocked", "chats", "users"]

    ID = -0x1e99be6c
    QUALNAME = "types.contacts.BlockedSlice"

    def __init__(self, *, count: int, blocked: List["raw.base.PeerBlocked"], chats: List["raw.base.Chat"], users: List["raw.base.User"]) -> None:
        self.count = count  # int
        self.blocked = blocked  # Vector<PeerBlocked>
        self.chats = chats  # Vector<Chat>
        self.users = users  # Vector<User>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        count = Int.read(data)
        
        blocked = TLObject.read(data)
        
        chats = TLObject.read(data)
        
        users = TLObject.read(data)
        
        return BlockedSlice(count=count, blocked=blocked, chats=chats, users=users)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Int(self.count))
        
        data.write(Vector(self.blocked))
        
        data.write(Vector(self.chats))
        
        data.write(Vector(self.users))
        
        return data.getvalue()

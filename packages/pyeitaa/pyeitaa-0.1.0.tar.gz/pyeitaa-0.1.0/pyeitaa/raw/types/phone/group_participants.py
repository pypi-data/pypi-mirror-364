from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class GroupParticipants(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.phone.GroupParticipants`.

    Details:
        - Layer: ``135``
        - ID: ``-0xb88ae4a``

    Parameters:
        count: ``int`` ``32-bit``
        participants: List of :obj:`GroupCallParticipant <pyeitaa.raw.base.GroupCallParticipant>`
        next_offset: ``str``
        chats: List of :obj:`Chat <pyeitaa.raw.base.Chat>`
        users: List of :obj:`User <pyeitaa.raw.base.User>`
        version: ``int`` ``32-bit``

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`phone.GetGroupParticipants <pyeitaa.raw.functions.phone.GetGroupParticipants>`
    """

    __slots__: List[str] = ["count", "participants", "next_offset", "chats", "users", "version"]

    ID = -0xb88ae4a
    QUALNAME = "types.phone.GroupParticipants"

    def __init__(self, *, count: int, participants: List["raw.base.GroupCallParticipant"], next_offset: str, chats: List["raw.base.Chat"], users: List["raw.base.User"], version: int) -> None:
        self.count = count  # int
        self.participants = participants  # Vector<GroupCallParticipant>
        self.next_offset = next_offset  # string
        self.chats = chats  # Vector<Chat>
        self.users = users  # Vector<User>
        self.version = version  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        count = Int.read(data)
        
        participants = TLObject.read(data)
        
        next_offset = String.read(data)
        
        chats = TLObject.read(data)
        
        users = TLObject.read(data)
        
        version = Int.read(data)
        
        return GroupParticipants(count=count, participants=participants, next_offset=next_offset, chats=chats, users=users, version=version)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Int(self.count))
        
        data.write(Vector(self.participants))
        
        data.write(String(self.next_offset))
        
        data.write(Vector(self.chats))
        
        data.write(Vector(self.users))
        
        data.write(Int(self.version))
        
        return data.getvalue()

from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class GroupCall(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.phone.GroupCall`.

    Details:
        - Layer: ``135``
        - ID: ``-0x618d8553``

    Parameters:
        call: :obj:`GroupCall <pyeitaa.raw.base.GroupCall>`
        participants: List of :obj:`GroupCallParticipant <pyeitaa.raw.base.GroupCallParticipant>`
        participants_next_offset: ``str``
        chats: List of :obj:`Chat <pyeitaa.raw.base.Chat>`
        users: List of :obj:`User <pyeitaa.raw.base.User>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`phone.GetGroupCall <pyeitaa.raw.functions.phone.GetGroupCall>`
    """

    __slots__: List[str] = ["call", "participants", "participants_next_offset", "chats", "users"]

    ID = -0x618d8553
    QUALNAME = "types.phone.GroupCall"

    def __init__(self, *, call: "raw.base.GroupCall", participants: List["raw.base.GroupCallParticipant"], participants_next_offset: str, chats: List["raw.base.Chat"], users: List["raw.base.User"]) -> None:
        self.call = call  # GroupCall
        self.participants = participants  # Vector<GroupCallParticipant>
        self.participants_next_offset = participants_next_offset  # string
        self.chats = chats  # Vector<Chat>
        self.users = users  # Vector<User>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        call = TLObject.read(data)
        
        participants = TLObject.read(data)
        
        participants_next_offset = String.read(data)
        
        chats = TLObject.read(data)
        
        users = TLObject.read(data)
        
        return GroupCall(call=call, participants=participants, participants_next_offset=participants_next_offset, chats=chats, users=users)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.call.write())
        
        data.write(Vector(self.participants))
        
        data.write(String(self.participants_next_offset))
        
        data.write(Vector(self.chats))
        
        data.write(Vector(self.users))
        
        return data.getvalue()

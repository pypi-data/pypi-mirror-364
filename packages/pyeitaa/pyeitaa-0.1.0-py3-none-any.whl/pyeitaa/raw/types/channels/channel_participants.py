from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class ChannelParticipants(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.channels.ChannelParticipants`.

    Details:
        - Layer: ``135``
        - ID: ``-0x654f0151``

    Parameters:
        count: ``int`` ``32-bit``
        participants: List of :obj:`ChannelParticipant <pyeitaa.raw.base.ChannelParticipant>`
        chats: List of :obj:`Chat <pyeitaa.raw.base.Chat>`
        users: List of :obj:`User <pyeitaa.raw.base.User>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`channels.GetParticipants <pyeitaa.raw.functions.channels.GetParticipants>`
    """

    __slots__: List[str] = ["count", "participants", "chats", "users"]

    ID = -0x654f0151
    QUALNAME = "types.channels.ChannelParticipants"

    def __init__(self, *, count: int, participants: List["raw.base.ChannelParticipant"], chats: List["raw.base.Chat"], users: List["raw.base.User"]) -> None:
        self.count = count  # int
        self.participants = participants  # Vector<ChannelParticipant>
        self.chats = chats  # Vector<Chat>
        self.users = users  # Vector<User>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        count = Int.read(data)
        
        participants = TLObject.read(data)
        
        chats = TLObject.read(data)
        
        users = TLObject.read(data)
        
        return ChannelParticipants(count=count, participants=participants, chats=chats, users=users)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Int(self.count))
        
        data.write(Vector(self.participants))
        
        data.write(Vector(self.chats))
        
        data.write(Vector(self.users))
        
        return data.getvalue()

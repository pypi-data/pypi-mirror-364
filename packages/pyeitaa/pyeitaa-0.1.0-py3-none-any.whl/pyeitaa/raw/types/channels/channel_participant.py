from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class ChannelParticipant(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.channels.ChannelParticipant`.

    Details:
        - Layer: ``135``
        - ID: ``-0x2047fce9``

    Parameters:
        participant: :obj:`ChannelParticipant <pyeitaa.raw.base.ChannelParticipant>`
        chats: List of :obj:`Chat <pyeitaa.raw.base.Chat>`
        users: List of :obj:`User <pyeitaa.raw.base.User>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`channels.GetParticipant <pyeitaa.raw.functions.channels.GetParticipant>`
    """

    __slots__: List[str] = ["participant", "chats", "users"]

    ID = -0x2047fce9
    QUALNAME = "types.channels.ChannelParticipant"

    def __init__(self, *, participant: "raw.base.ChannelParticipant", chats: List["raw.base.Chat"], users: List["raw.base.User"]) -> None:
        self.participant = participant  # ChannelParticipant
        self.chats = chats  # Vector<Chat>
        self.users = users  # Vector<User>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        participant = TLObject.read(data)
        
        chats = TLObject.read(data)
        
        users = TLObject.read(data)
        
        return ChannelParticipant(participant=participant, chats=chats, users=users)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.participant.write())
        
        data.write(Vector(self.chats))
        
        data.write(Vector(self.users))
        
        return data.getvalue()

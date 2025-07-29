from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class VotesList(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.messages.VotesList`.

    Details:
        - Layer: ``135``
        - ID: ``0x823f649``

    Parameters:
        count: ``int`` ``32-bit``
        votes: List of :obj:`MessageUserVote <pyeitaa.raw.base.MessageUserVote>`
        users: List of :obj:`User <pyeitaa.raw.base.User>`
        next_offset (optional): ``str``

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`messages.GetPollVotes <pyeitaa.raw.functions.messages.GetPollVotes>`
    """

    __slots__: List[str] = ["count", "votes", "users", "next_offset"]

    ID = 0x823f649
    QUALNAME = "types.messages.VotesList"

    def __init__(self, *, count: int, votes: List["raw.base.MessageUserVote"], users: List["raw.base.User"], next_offset: Optional[str] = None) -> None:
        self.count = count  # int
        self.votes = votes  # Vector<MessageUserVote>
        self.users = users  # Vector<User>
        self.next_offset = next_offset  # flags.0?string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        count = Int.read(data)
        
        votes = TLObject.read(data)
        
        users = TLObject.read(data)
        
        next_offset = String.read(data) if flags & (1 << 0) else None
        return VotesList(count=count, votes=votes, users=users, next_offset=next_offset)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.next_offset is not None else 0
        data.write(Int(flags))
        
        data.write(Int(self.count))
        
        data.write(Vector(self.votes))
        
        data.write(Vector(self.users))
        
        if self.next_offset is not None:
            data.write(String(self.next_offset))
        
        return data.getvalue()

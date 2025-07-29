from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class ResolvedPeer(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.contacts.ResolvedPeer`.

    Details:
        - Layer: ``135``
        - ID: ``0x7f077ad9``

    Parameters:
        peer: :obj:`Peer <pyeitaa.raw.base.Peer>`
        chats: List of :obj:`Chat <pyeitaa.raw.base.Chat>`
        users: List of :obj:`User <pyeitaa.raw.base.User>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`contacts.ResolveUsername <pyeitaa.raw.functions.contacts.ResolveUsername>`
    """

    __slots__: List[str] = ["peer", "chats", "users"]

    ID = 0x7f077ad9
    QUALNAME = "types.contacts.ResolvedPeer"

    def __init__(self, *, peer: "raw.base.Peer", chats: List["raw.base.Chat"], users: List["raw.base.User"]) -> None:
        self.peer = peer  # Peer
        self.chats = chats  # Vector<Chat>
        self.users = users  # Vector<User>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        peer = TLObject.read(data)
        
        chats = TLObject.read(data)
        
        users = TLObject.read(data)
        
        return ResolvedPeer(peer=peer, chats=chats, users=users)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.peer.write())
        
        data.write(Vector(self.chats))
        
        data.write(Vector(self.users))
        
        return data.getvalue()

from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class JoinAsPeers(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.phone.JoinAsPeers`.

    Details:
        - Layer: ``135``
        - ID: ``-0x501a9dc1``

    Parameters:
        peers: List of :obj:`Peer <pyeitaa.raw.base.Peer>`
        chats: List of :obj:`Chat <pyeitaa.raw.base.Chat>`
        users: List of :obj:`User <pyeitaa.raw.base.User>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`phone.GetGroupCallJoinAs <pyeitaa.raw.functions.phone.GetGroupCallJoinAs>`
    """

    __slots__: List[str] = ["peers", "chats", "users"]

    ID = -0x501a9dc1
    QUALNAME = "types.phone.JoinAsPeers"

    def __init__(self, *, peers: List["raw.base.Peer"], chats: List["raw.base.Chat"], users: List["raw.base.User"]) -> None:
        self.peers = peers  # Vector<Peer>
        self.chats = chats  # Vector<Chat>
        self.users = users  # Vector<User>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        peers = TLObject.read(data)
        
        chats = TLObject.read(data)
        
        users = TLObject.read(data)
        
        return JoinAsPeers(peers=peers, chats=chats, users=users)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Vector(self.peers))
        
        data.write(Vector(self.chats))
        
        data.write(Vector(self.users))
        
        return data.getvalue()

from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class TopPeers(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.contacts.TopPeers`.

    Details:
        - Layer: ``135``
        - ID: ``0x70b772a8``

    Parameters:
        categories: List of :obj:`TopPeerCategoryPeers <pyeitaa.raw.base.TopPeerCategoryPeers>`
        chats: List of :obj:`Chat <pyeitaa.raw.base.Chat>`
        users: List of :obj:`User <pyeitaa.raw.base.User>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`contacts.GetTopPeers <pyeitaa.raw.functions.contacts.GetTopPeers>`
    """

    __slots__: List[str] = ["categories", "chats", "users"]

    ID = 0x70b772a8
    QUALNAME = "types.contacts.TopPeers"

    def __init__(self, *, categories: List["raw.base.TopPeerCategoryPeers"], chats: List["raw.base.Chat"], users: List["raw.base.User"]) -> None:
        self.categories = categories  # Vector<TopPeerCategoryPeers>
        self.chats = chats  # Vector<Chat>
        self.users = users  # Vector<User>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        categories = TLObject.read(data)
        
        chats = TLObject.read(data)
        
        users = TLObject.read(data)
        
        return TopPeers(categories=categories, chats=chats, users=users)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Vector(self.categories))
        
        data.write(Vector(self.chats))
        
        data.write(Vector(self.users))
        
        return data.getvalue()

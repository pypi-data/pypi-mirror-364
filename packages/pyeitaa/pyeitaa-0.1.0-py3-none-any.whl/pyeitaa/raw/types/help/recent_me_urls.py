from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class RecentMeUrls(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.help.RecentMeUrls`.

    Details:
        - Layer: ``135``
        - ID: ``0xe0310d7``

    Parameters:
        urls: List of :obj:`RecentMeUrl <pyeitaa.raw.base.RecentMeUrl>`
        chats: List of :obj:`Chat <pyeitaa.raw.base.Chat>`
        users: List of :obj:`User <pyeitaa.raw.base.User>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`help.GetRecentMeUrls <pyeitaa.raw.functions.help.GetRecentMeUrls>`
    """

    __slots__: List[str] = ["urls", "chats", "users"]

    ID = 0xe0310d7
    QUALNAME = "types.help.RecentMeUrls"

    def __init__(self, *, urls: List["raw.base.RecentMeUrl"], chats: List["raw.base.Chat"], users: List["raw.base.User"]) -> None:
        self.urls = urls  # Vector<RecentMeUrl>
        self.chats = chats  # Vector<Chat>
        self.users = users  # Vector<User>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        urls = TLObject.read(data)
        
        chats = TLObject.read(data)
        
        users = TLObject.read(data)
        
        return RecentMeUrls(urls=urls, chats=chats, users=users)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Vector(self.urls))
        
        data.write(Vector(self.chats))
        
        data.write(Vector(self.users))
        
        return data.getvalue()

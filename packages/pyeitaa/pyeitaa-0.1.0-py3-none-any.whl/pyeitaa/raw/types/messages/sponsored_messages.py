from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class SponsoredMessages(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.messages.SponsoredMessages`.

    Details:
        - Layer: ``135``
        - ID: ``0x65a4c7d5``

    Parameters:
        messages: List of :obj:`SponsoredMessage <pyeitaa.raw.base.SponsoredMessage>`
        chats: List of :obj:`Chat <pyeitaa.raw.base.Chat>`
        users: List of :obj:`User <pyeitaa.raw.base.User>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`channels.GetSponsoredMessages <pyeitaa.raw.functions.channels.GetSponsoredMessages>`
    """

    __slots__: List[str] = ["messages", "chats", "users"]

    ID = 0x65a4c7d5
    QUALNAME = "types.messages.SponsoredMessages"

    def __init__(self, *, messages: List["raw.base.SponsoredMessage"], chats: List["raw.base.Chat"], users: List["raw.base.User"]) -> None:
        self.messages = messages  # Vector<SponsoredMessage>
        self.chats = chats  # Vector<Chat>
        self.users = users  # Vector<User>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        messages = TLObject.read(data)
        
        chats = TLObject.read(data)
        
        users = TLObject.read(data)
        
        return SponsoredMessages(messages=messages, chats=chats, users=users)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Vector(self.messages))
        
        data.write(Vector(self.chats))
        
        data.write(Vector(self.users))
        
        return data.getvalue()

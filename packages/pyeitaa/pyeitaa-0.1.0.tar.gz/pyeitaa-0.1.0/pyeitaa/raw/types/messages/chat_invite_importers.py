from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class ChatInviteImporters(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.messages.ChatInviteImporters`.

    Details:
        - Layer: ``135``
        - ID: ``-0x7e494ff6``

    Parameters:
        count: ``int`` ``32-bit``
        importers: List of :obj:`ChatInviteImporter <pyeitaa.raw.base.ChatInviteImporter>`
        users: List of :obj:`User <pyeitaa.raw.base.User>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`messages.GetChatInviteImporters <pyeitaa.raw.functions.messages.GetChatInviteImporters>`
    """

    __slots__: List[str] = ["count", "importers", "users"]

    ID = -0x7e494ff6
    QUALNAME = "types.messages.ChatInviteImporters"

    def __init__(self, *, count: int, importers: List["raw.base.ChatInviteImporter"], users: List["raw.base.User"]) -> None:
        self.count = count  # int
        self.importers = importers  # Vector<ChatInviteImporter>
        self.users = users  # Vector<User>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        count = Int.read(data)
        
        importers = TLObject.read(data)
        
        users = TLObject.read(data)
        
        return ChatInviteImporters(count=count, importers=importers, users=users)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Int(self.count))
        
        data.write(Vector(self.importers))
        
        data.write(Vector(self.users))
        
        return data.getvalue()

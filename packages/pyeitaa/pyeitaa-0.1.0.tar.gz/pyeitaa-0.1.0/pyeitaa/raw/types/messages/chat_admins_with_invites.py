from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class ChatAdminsWithInvites(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.messages.ChatAdminsWithInvites`.

    Details:
        - Layer: ``135``
        - ID: ``-0x49648d29``

    Parameters:
        admins: List of :obj:`ChatAdminWithInvites <pyeitaa.raw.base.ChatAdminWithInvites>`
        users: List of :obj:`User <pyeitaa.raw.base.User>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`messages.GetAdminsWithInvites <pyeitaa.raw.functions.messages.GetAdminsWithInvites>`
    """

    __slots__: List[str] = ["admins", "users"]

    ID = -0x49648d29
    QUALNAME = "types.messages.ChatAdminsWithInvites"

    def __init__(self, *, admins: List["raw.base.ChatAdminWithInvites"], users: List["raw.base.User"]) -> None:
        self.admins = admins  # Vector<ChatAdminWithInvites>
        self.users = users  # Vector<User>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        admins = TLObject.read(data)
        
        users = TLObject.read(data)
        
        return ChatAdminsWithInvites(admins=admins, users=users)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Vector(self.admins))
        
        data.write(Vector(self.users))
        
        return data.getvalue()

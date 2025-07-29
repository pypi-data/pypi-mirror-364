from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class ExportedChatInviteReplaced(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.messages.ExportedChatInvite`.

    Details:
        - Layer: ``135``
        - ID: ``0x222600ef``

    Parameters:
        invite: :obj:`ExportedChatInvite <pyeitaa.raw.base.ExportedChatInvite>`
        new_invite: :obj:`ExportedChatInvite <pyeitaa.raw.base.ExportedChatInvite>`
        users: List of :obj:`User <pyeitaa.raw.base.User>`

    See Also:
        This object can be returned by 2 methods:

        .. hlist::
            :columns: 2

            - :obj:`messages.GetExportedChatInvite <pyeitaa.raw.functions.messages.GetExportedChatInvite>`
            - :obj:`messages.EditExportedChatInvite <pyeitaa.raw.functions.messages.EditExportedChatInvite>`
    """

    __slots__: List[str] = ["invite", "new_invite", "users"]

    ID = 0x222600ef
    QUALNAME = "types.messages.ExportedChatInviteReplaced"

    def __init__(self, *, invite: "raw.base.ExportedChatInvite", new_invite: "raw.base.ExportedChatInvite", users: List["raw.base.User"]) -> None:
        self.invite = invite  # ExportedChatInvite
        self.new_invite = new_invite  # ExportedChatInvite
        self.users = users  # Vector<User>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        invite = TLObject.read(data)
        
        new_invite = TLObject.read(data)
        
        users = TLObject.read(data)
        
        return ExportedChatInviteReplaced(invite=invite, new_invite=new_invite, users=users)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.invite.write())
        
        data.write(self.new_invite.write())
        
        data.write(Vector(self.users))
        
        return data.getvalue()

from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class ExportedChatInvite(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.messages.ExportedChatInvite`.

    Details:
        - Layer: ``135``
        - ID: ``0x1871be50``

    Parameters:
        invite: :obj:`ExportedChatInvite <pyeitaa.raw.base.ExportedChatInvite>`
        users: List of :obj:`User <pyeitaa.raw.base.User>`

    See Also:
        This object can be returned by 2 methods:

        .. hlist::
            :columns: 2

            - :obj:`messages.GetExportedChatInvite <pyeitaa.raw.functions.messages.GetExportedChatInvite>`
            - :obj:`messages.EditExportedChatInvite <pyeitaa.raw.functions.messages.EditExportedChatInvite>`
    """

    __slots__: List[str] = ["invite", "users"]

    ID = 0x1871be50
    QUALNAME = "types.messages.ExportedChatInvite"

    def __init__(self, *, invite: "raw.base.ExportedChatInvite", users: List["raw.base.User"]) -> None:
        self.invite = invite  # ExportedChatInvite
        self.users = users  # Vector<User>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        invite = TLObject.read(data)
        
        users = TLObject.read(data)
        
        return ExportedChatInvite(invite=invite, users=users)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.invite.write())
        
        data.write(Vector(self.users))
        
        return data.getvalue()

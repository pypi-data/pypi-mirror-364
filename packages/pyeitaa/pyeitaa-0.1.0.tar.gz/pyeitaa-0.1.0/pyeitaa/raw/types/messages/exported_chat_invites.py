from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class ExportedChatInvites(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.messages.ExportedChatInvites`.

    Details:
        - Layer: ``135``
        - ID: ``-0x4239d234``

    Parameters:
        count: ``int`` ``32-bit``
        invites: List of :obj:`ExportedChatInvite <pyeitaa.raw.base.ExportedChatInvite>`
        users: List of :obj:`User <pyeitaa.raw.base.User>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`messages.GetExportedChatInvites <pyeitaa.raw.functions.messages.GetExportedChatInvites>`
    """

    __slots__: List[str] = ["count", "invites", "users"]

    ID = -0x4239d234
    QUALNAME = "types.messages.ExportedChatInvites"

    def __init__(self, *, count: int, invites: List["raw.base.ExportedChatInvite"], users: List["raw.base.User"]) -> None:
        self.count = count  # int
        self.invites = invites  # Vector<ExportedChatInvite>
        self.users = users  # Vector<User>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        count = Int.read(data)
        
        invites = TLObject.read(data)
        
        users = TLObject.read(data)
        
        return ExportedChatInvites(count=count, invites=invites, users=users)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Int(self.count))
        
        data.write(Vector(self.invites))
        
        data.write(Vector(self.users))
        
        return data.getvalue()

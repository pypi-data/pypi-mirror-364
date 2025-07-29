from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class ChatAdminWithInvites(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.ChatAdminWithInvites`.

    Details:
        - Layer: ``135``
        - ID: ``-0xd1310dd``

    Parameters:
        admin_id: ``int`` ``64-bit``
        invites_count: ``int`` ``32-bit``
        revoked_invites_count: ``int`` ``32-bit``
    """

    __slots__: List[str] = ["admin_id", "invites_count", "revoked_invites_count"]

    ID = -0xd1310dd
    QUALNAME = "types.ChatAdminWithInvites"

    def __init__(self, *, admin_id: int, invites_count: int, revoked_invites_count: int) -> None:
        self.admin_id = admin_id  # long
        self.invites_count = invites_count  # int
        self.revoked_invites_count = revoked_invites_count  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        admin_id = Long.read(data)
        
        invites_count = Int.read(data)
        
        revoked_invites_count = Int.read(data)
        
        return ChatAdminWithInvites(admin_id=admin_id, invites_count=invites_count, revoked_invites_count=revoked_invites_count)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Long(self.admin_id))
        
        data.write(Int(self.invites_count))
        
        data.write(Int(self.revoked_invites_count))
        
        return data.getvalue()

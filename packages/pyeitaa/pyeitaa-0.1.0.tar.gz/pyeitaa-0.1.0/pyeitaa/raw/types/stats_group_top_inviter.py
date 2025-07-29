from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class StatsGroupTopInviter(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.StatsGroupTopInviter`.

    Details:
        - Layer: ``135``
        - ID: ``0x535f779d``

    Parameters:
        user_id: ``int`` ``64-bit``
        invitations: ``int`` ``32-bit``
    """

    __slots__: List[str] = ["user_id", "invitations"]

    ID = 0x535f779d
    QUALNAME = "types.StatsGroupTopInviter"

    def __init__(self, *, user_id: int, invitations: int) -> None:
        self.user_id = user_id  # long
        self.invitations = invitations  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        user_id = Long.read(data)
        
        invitations = Int.read(data)
        
        return StatsGroupTopInviter(user_id=user_id, invitations=invitations)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Long(self.user_id))
        
        data.write(Int(self.invitations))
        
        return data.getvalue()

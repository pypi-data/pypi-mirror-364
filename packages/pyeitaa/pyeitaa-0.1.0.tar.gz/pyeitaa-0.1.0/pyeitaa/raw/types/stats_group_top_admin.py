from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class StatsGroupTopAdmin(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.StatsGroupTopAdmin`.

    Details:
        - Layer: ``135``
        - ID: ``-0x28a7b379``

    Parameters:
        user_id: ``int`` ``64-bit``
        deleted: ``int`` ``32-bit``
        kicked: ``int`` ``32-bit``
        banned: ``int`` ``32-bit``
    """

    __slots__: List[str] = ["user_id", "deleted", "kicked", "banned"]

    ID = -0x28a7b379
    QUALNAME = "types.StatsGroupTopAdmin"

    def __init__(self, *, user_id: int, deleted: int, kicked: int, banned: int) -> None:
        self.user_id = user_id  # long
        self.deleted = deleted  # int
        self.kicked = kicked  # int
        self.banned = banned  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        user_id = Long.read(data)
        
        deleted = Int.read(data)
        
        kicked = Int.read(data)
        
        banned = Int.read(data)
        
        return StatsGroupTopAdmin(user_id=user_id, deleted=deleted, kicked=kicked, banned=banned)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Long(self.user_id))
        
        data.write(Int(self.deleted))
        
        data.write(Int(self.kicked))
        
        data.write(Int(self.banned))
        
        return data.getvalue()

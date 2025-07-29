from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class GroupCallDiscarded(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.GroupCall`.

    Details:
        - Layer: ``135``
        - ID: ``0x7780bcb4``

    Parameters:
        id: ``int`` ``64-bit``
        access_hash: ``int`` ``64-bit``
        duration: ``int`` ``32-bit``
    """

    __slots__: List[str] = ["id", "access_hash", "duration"]

    ID = 0x7780bcb4
    QUALNAME = "types.GroupCallDiscarded"

    def __init__(self, *, id: int, access_hash: int, duration: int) -> None:
        self.id = id  # long
        self.access_hash = access_hash  # long
        self.duration = duration  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        id = Long.read(data)
        
        access_hash = Long.read(data)
        
        duration = Int.read(data)
        
        return GroupCallDiscarded(id=id, access_hash=access_hash, duration=duration)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Long(self.id))
        
        data.write(Long(self.access_hash))
        
        data.write(Int(self.duration))
        
        return data.getvalue()

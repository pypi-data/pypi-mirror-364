from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class UpdateMessageID(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.Update`.

    Details:
        - Layer: ``135``
        - ID: ``0x4e90bfd6``

    Parameters:
        id: ``int`` ``32-bit``
        random_id: ``int`` ``64-bit``
    """

    __slots__: List[str] = ["id", "random_id"]

    ID = 0x4e90bfd6
    QUALNAME = "types.UpdateMessageID"

    def __init__(self, *, id: int, random_id: int) -> None:
        self.id = id  # int
        self.random_id = random_id  # long

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        id = Int.read(data)
        
        random_id = Long.read(data)
        
        return UpdateMessageID(id=id, random_id=random_id)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Int(self.id))
        
        data.write(Long(self.random_id))
        
        return data.getvalue()

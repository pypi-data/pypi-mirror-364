from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class PhotoEmpty(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.Photo`.

    Details:
        - Layer: ``135``
        - ID: ``0x2331b22d``

    Parameters:
        id: ``int`` ``64-bit``
    """

    __slots__: List[str] = ["id"]

    ID = 0x2331b22d
    QUALNAME = "types.PhotoEmpty"

    def __init__(self, *, id: int) -> None:
        self.id = id  # long

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        id = Long.read(data)
        
        return PhotoEmpty(id=id)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Long(self.id))
        
        return data.getvalue()

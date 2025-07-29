from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class DocumentAttributeImageSize(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.DocumentAttribute`.

    Details:
        - Layer: ``135``
        - ID: ``0x6c37c15c``

    Parameters:
        w: ``int`` ``32-bit``
        h: ``int`` ``32-bit``
    """

    __slots__: List[str] = ["w", "h"]

    ID = 0x6c37c15c
    QUALNAME = "types.DocumentAttributeImageSize"

    def __init__(self, *, w: int, h: int) -> None:
        self.w = w  # int
        self.h = h  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        w = Int.read(data)
        
        h = Int.read(data)
        
        return DocumentAttributeImageSize(w=w, h=h)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Int(self.w))
        
        data.write(Int(self.h))
        
        return data.getvalue()

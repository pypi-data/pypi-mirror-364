from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String, Vector
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class PhotoSizeProgressive(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.PhotoSize`.

    Details:
        - Layer: ``135``
        - ID: ``-0x5c1046b``

    Parameters:
        type: ``str``
        w: ``int`` ``32-bit``
        h: ``int`` ``32-bit``
        sizes: List of ``int`` ``32-bit``
    """

    __slots__: List[str] = ["type", "w", "h", "sizes"]

    ID = -0x5c1046b
    QUALNAME = "types.PhotoSizeProgressive"

    def __init__(self, *, type: str, w: int, h: int, sizes: List[int]) -> None:
        self.type = type  # string
        self.w = w  # int
        self.h = h  # int
        self.sizes = sizes  # Vector<int>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        type = String.read(data)
        
        w = Int.read(data)
        
        h = Int.read(data)
        
        sizes = TLObject.read(data, Int)
        
        return PhotoSizeProgressive(type=type, w=w, h=h, sizes=sizes)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(String(self.type))
        
        data.write(Int(self.w))
        
        data.write(Int(self.h))
        
        data.write(Vector(self.sizes, Int))
        
        return data.getvalue()

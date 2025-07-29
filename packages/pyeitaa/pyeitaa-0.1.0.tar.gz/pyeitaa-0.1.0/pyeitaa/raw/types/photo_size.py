from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class PhotoSize(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.PhotoSize`.

    Details:
        - Layer: ``135``
        - ID: ``0x77bfb61b``

    Parameters:
        type: ``str``
        location: :obj:`FileLocation <pyeitaa.raw.base.FileLocation>`
        w: ``int`` ``32-bit``
        h: ``int`` ``32-bit``
        size: ``int`` ``32-bit``
    """

    __slots__: List[str] = ["type", "location", "w", "h", "size"]

    ID = 0x77bfb61b
    QUALNAME = "types.PhotoSize"

    def __init__(self, *, type: str, location: "raw.base.FileLocation", w: int, h: int, size: int) -> None:
        self.type = type  # string
        self.location = location  # FileLocation
        self.w = w  # int
        self.h = h  # int
        self.size = size  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        type = String.read(data)
        
        location = TLObject.read(data)
        
        w = Int.read(data)
        
        h = Int.read(data)
        
        size = Int.read(data)
        
        return PhotoSize(type=type, location=location, w=w, h=h, size=size)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(String(self.type))
        
        data.write(self.location.write())
        
        data.write(Int(self.w))
        
        data.write(Int(self.h))
        
        data.write(Int(self.size))
        
        return data.getvalue()

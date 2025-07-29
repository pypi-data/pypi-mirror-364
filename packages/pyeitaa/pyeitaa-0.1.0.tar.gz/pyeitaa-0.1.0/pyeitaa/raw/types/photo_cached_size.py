from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Bytes, String
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class PhotoCachedSize(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.PhotoSize`.

    Details:
        - Layer: ``135``
        - ID: ``-0x1658cb06``

    Parameters:
        type: ``str``
        location: :obj:`FileLocation <pyeitaa.raw.base.FileLocation>`
        w: ``int`` ``32-bit``
        h: ``int`` ``32-bit``
        bytes: ``bytes``
    """

    __slots__: List[str] = ["type", "location", "w", "h", "bytes"]

    ID = -0x1658cb06
    QUALNAME = "types.PhotoCachedSize"

    def __init__(self, *, type: str, location: "raw.base.FileLocation", w: int, h: int, bytes: bytes) -> None:
        self.type = type  # string
        self.location = location  # FileLocation
        self.w = w  # int
        self.h = h  # int
        self.bytes = bytes  # bytes

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        type = String.read(data)
        
        location = TLObject.read(data)
        
        w = Int.read(data)
        
        h = Int.read(data)
        
        bytes = Bytes.read(data)
        
        return PhotoCachedSize(type=type, location=location, w=w, h=h, bytes=bytes)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(String(self.type))
        
        data.write(self.location.write())
        
        data.write(Int(self.w))
        
        data.write(Int(self.h))
        
        data.write(Bytes(self.bytes))
        
        return data.getvalue()

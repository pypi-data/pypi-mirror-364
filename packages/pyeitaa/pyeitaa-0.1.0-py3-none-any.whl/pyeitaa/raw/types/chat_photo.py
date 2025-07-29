from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class ChatPhoto(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.ChatPhoto`.

    Details:
        - Layer: ``135``
        - ID: ``0x6153276a``

    Parameters:
        photo_small: :obj:`FileLocation <pyeitaa.raw.base.FileLocation>`
        photo_big: :obj:`FileLocation <pyeitaa.raw.base.FileLocation>`
    """

    __slots__: List[str] = ["photo_small", "photo_big"]

    ID = 0x6153276a
    QUALNAME = "types.ChatPhoto"

    def __init__(self, *, photo_small: "raw.base.FileLocation", photo_big: "raw.base.FileLocation") -> None:
        self.photo_small = photo_small  # FileLocation
        self.photo_big = photo_big  # FileLocation

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        photo_small = TLObject.read(data)
        
        photo_big = TLObject.read(data)
        
        return ChatPhoto(photo_small=photo_small, photo_big=photo_big)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.photo_small.write())
        
        data.write(self.photo_big.write())
        
        return data.getvalue()

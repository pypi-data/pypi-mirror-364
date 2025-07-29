from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class UserProfilePhoto(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.UserProfilePhoto`.

    Details:
        - Layer: ``135``
        - ID: ``0x69d3ab26``

    Parameters:
        photo_id: ``int`` ``64-bit``
        photo_small: :obj:`FileLocation <pyeitaa.raw.base.FileLocation>`
        photo_big: :obj:`FileLocation <pyeitaa.raw.base.FileLocation>`
        dc_id: ``int`` ``32-bit``
        has_video (optional): ``bool``
    """

    __slots__: List[str] = ["photo_id", "photo_small", "photo_big", "dc_id", "has_video"]

    ID = 0x69d3ab26
    QUALNAME = "types.UserProfilePhoto"

    def __init__(self, *, photo_id: int, photo_small: "raw.base.FileLocation", photo_big: "raw.base.FileLocation", dc_id: int, has_video: Optional[bool] = None) -> None:
        self.photo_id = photo_id  # long
        self.photo_small = photo_small  # FileLocation
        self.photo_big = photo_big  # FileLocation
        self.dc_id = dc_id  # int
        self.has_video = has_video  # flags.0?true

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        has_video = True if flags & (1 << 0) else False
        photo_id = Long.read(data)
        
        photo_small = TLObject.read(data)
        
        photo_big = TLObject.read(data)
        
        dc_id = Int.read(data)
        
        return UserProfilePhoto(photo_id=photo_id, photo_small=photo_small, photo_big=photo_big, dc_id=dc_id, has_video=has_video)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.has_video else 0
        data.write(Int(flags))
        
        data.write(Long(self.photo_id))
        
        data.write(self.photo_small.write())
        
        data.write(self.photo_big.write())
        
        data.write(Int(self.dc_id))
        
        return data.getvalue()

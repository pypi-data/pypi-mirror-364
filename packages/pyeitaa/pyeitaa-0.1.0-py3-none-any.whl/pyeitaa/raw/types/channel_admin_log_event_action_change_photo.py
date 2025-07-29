from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class ChannelAdminLogEventActionChangePhoto(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.ChannelAdminLogEventAction`.

    Details:
        - Layer: ``135``
        - ID: ``0x434bd2af``

    Parameters:
        prev_photo: :obj:`Photo <pyeitaa.raw.base.Photo>`
        new_photo: :obj:`Photo <pyeitaa.raw.base.Photo>`
    """

    __slots__: List[str] = ["prev_photo", "new_photo"]

    ID = 0x434bd2af
    QUALNAME = "types.ChannelAdminLogEventActionChangePhoto"

    def __init__(self, *, prev_photo: "raw.base.Photo", new_photo: "raw.base.Photo") -> None:
        self.prev_photo = prev_photo  # Photo
        self.new_photo = new_photo  # Photo

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        prev_photo = TLObject.read(data)
        
        new_photo = TLObject.read(data)
        
        return ChannelAdminLogEventActionChangePhoto(prev_photo=prev_photo, new_photo=new_photo)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.prev_photo.write())
        
        data.write(self.new_photo.write())
        
        return data.getvalue()

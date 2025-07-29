from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class MessageMediaPhoto(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.MessageMedia`.

    Details:
        - Layer: ``135``
        - ID: ``0x695150d7``

    Parameters:
        photo (optional): :obj:`Photo <pyeitaa.raw.base.Photo>`
        ttl_seconds (optional): ``int`` ``32-bit``

    See Also:
        This object can be returned by 3 methods:

        .. hlist::
            :columns: 2

            - :obj:`messages.GetWebPagePreview <pyeitaa.raw.functions.messages.GetWebPagePreview>`
            - :obj:`messages.UploadMedia <pyeitaa.raw.functions.messages.UploadMedia>`
            - :obj:`messages.UploadImportedMedia <pyeitaa.raw.functions.messages.UploadImportedMedia>`
    """

    __slots__: List[str] = ["photo", "ttl_seconds"]

    ID = 0x695150d7
    QUALNAME = "types.MessageMediaPhoto"

    def __init__(self, *, photo: "raw.base.Photo" = None, ttl_seconds: Optional[int] = None) -> None:
        self.photo = photo  # flags.0?Photo
        self.ttl_seconds = ttl_seconds  # flags.2?int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        photo = TLObject.read(data) if flags & (1 << 0) else None
        
        ttl_seconds = Int.read(data) if flags & (1 << 2) else None
        return MessageMediaPhoto(photo=photo, ttl_seconds=ttl_seconds)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.photo is not None else 0
        flags |= (1 << 2) if self.ttl_seconds is not None else 0
        data.write(Int(flags))
        
        if self.photo is not None:
            data.write(self.photo.write())
        
        if self.ttl_seconds is not None:
            data.write(Int(self.ttl_seconds))
        
        return data.getvalue()

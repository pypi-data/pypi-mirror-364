from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, String
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class PageBlockPhoto(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.PageBlock`.

    Details:
        - Layer: ``135``
        - ID: ``0x1759c560``

    Parameters:
        photo_id: ``int`` ``64-bit``
        caption: :obj:`PageCaption <pyeitaa.raw.base.PageCaption>`
        url (optional): ``str``
        webpage_id (optional): ``int`` ``64-bit``
    """

    __slots__: List[str] = ["photo_id", "caption", "url", "webpage_id"]

    ID = 0x1759c560
    QUALNAME = "types.PageBlockPhoto"

    def __init__(self, *, photo_id: int, caption: "raw.base.PageCaption", url: Optional[str] = None, webpage_id: Optional[int] = None) -> None:
        self.photo_id = photo_id  # long
        self.caption = caption  # PageCaption
        self.url = url  # flags.0?string
        self.webpage_id = webpage_id  # flags.0?long

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        photo_id = Long.read(data)
        
        caption = TLObject.read(data)
        
        url = String.read(data) if flags & (1 << 0) else None
        webpage_id = Long.read(data) if flags & (1 << 0) else None
        return PageBlockPhoto(photo_id=photo_id, caption=caption, url=url, webpage_id=webpage_id)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.url is not None else 0
        flags |= (1 << 0) if self.webpage_id is not None else 0
        data.write(Int(flags))
        
        data.write(Long(self.photo_id))
        
        data.write(self.caption.write())
        
        if self.url is not None:
            data.write(String(self.url))
        
        if self.webpage_id is not None:
            data.write(Long(self.webpage_id))
        
        return data.getvalue()

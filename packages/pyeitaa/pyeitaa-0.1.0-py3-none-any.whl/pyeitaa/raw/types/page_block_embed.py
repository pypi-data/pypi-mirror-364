from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, String
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class PageBlockEmbed(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.PageBlock`.

    Details:
        - Layer: ``135``
        - ID: ``-0x578e723b``

    Parameters:
        caption: :obj:`PageCaption <pyeitaa.raw.base.PageCaption>`
        full_width (optional): ``bool``
        allow_scrolling (optional): ``bool``
        url (optional): ``str``
        html (optional): ``str``
        poster_photo_id (optional): ``int`` ``64-bit``
        w (optional): ``int`` ``32-bit``
        h (optional): ``int`` ``32-bit``
    """

    __slots__: List[str] = ["caption", "full_width", "allow_scrolling", "url", "html", "poster_photo_id", "w", "h"]

    ID = -0x578e723b
    QUALNAME = "types.PageBlockEmbed"

    def __init__(self, *, caption: "raw.base.PageCaption", full_width: Optional[bool] = None, allow_scrolling: Optional[bool] = None, url: Optional[str] = None, html: Optional[str] = None, poster_photo_id: Optional[int] = None, w: Optional[int] = None, h: Optional[int] = None) -> None:
        self.caption = caption  # PageCaption
        self.full_width = full_width  # flags.0?true
        self.allow_scrolling = allow_scrolling  # flags.3?true
        self.url = url  # flags.1?string
        self.html = html  # flags.2?string
        self.poster_photo_id = poster_photo_id  # flags.4?long
        self.w = w  # flags.5?int
        self.h = h  # flags.5?int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        full_width = True if flags & (1 << 0) else False
        allow_scrolling = True if flags & (1 << 3) else False
        url = String.read(data) if flags & (1 << 1) else None
        html = String.read(data) if flags & (1 << 2) else None
        poster_photo_id = Long.read(data) if flags & (1 << 4) else None
        w = Int.read(data) if flags & (1 << 5) else None
        h = Int.read(data) if flags & (1 << 5) else None
        caption = TLObject.read(data)
        
        return PageBlockEmbed(caption=caption, full_width=full_width, allow_scrolling=allow_scrolling, url=url, html=html, poster_photo_id=poster_photo_id, w=w, h=h)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.full_width else 0
        flags |= (1 << 3) if self.allow_scrolling else 0
        flags |= (1 << 1) if self.url is not None else 0
        flags |= (1 << 2) if self.html is not None else 0
        flags |= (1 << 4) if self.poster_photo_id is not None else 0
        flags |= (1 << 5) if self.w is not None else 0
        flags |= (1 << 5) if self.h is not None else 0
        data.write(Int(flags))
        
        if self.url is not None:
            data.write(String(self.url))
        
        if self.html is not None:
            data.write(String(self.html))
        
        if self.poster_photo_id is not None:
            data.write(Long(self.poster_photo_id))
        
        if self.w is not None:
            data.write(Int(self.w))
        
        if self.h is not None:
            data.write(Int(self.h))
        
        data.write(self.caption.write())
        
        return data.getvalue()

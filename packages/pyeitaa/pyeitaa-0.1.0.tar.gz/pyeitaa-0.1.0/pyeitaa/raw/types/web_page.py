from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, String, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class WebPage(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.WebPage`.

    Details:
        - Layer: ``135``
        - ID: ``-0x1763ba4e``

    Parameters:
        id: ``int`` ``64-bit``
        url: ``str``
        display_url: ``str``
        hash: ``int`` ``32-bit``
        type (optional): ``str``
        site_name (optional): ``str``
        title (optional): ``str``
        description (optional): ``str``
        photo (optional): :obj:`Photo <pyeitaa.raw.base.Photo>`
        embed_url (optional): ``str``
        embed_type (optional): ``str``
        embed_width (optional): ``int`` ``32-bit``
        embed_height (optional): ``int`` ``32-bit``
        duration (optional): ``int`` ``32-bit``
        author (optional): ``str``
        document (optional): :obj:`Document <pyeitaa.raw.base.Document>`
        cached_page (optional): :obj:`Page <pyeitaa.raw.base.Page>`
        attributes (optional): List of :obj:`WebPageAttribute <pyeitaa.raw.base.WebPageAttribute>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`messages.GetWebPage <pyeitaa.raw.functions.messages.GetWebPage>`
    """

    __slots__: List[str] = ["id", "url", "display_url", "hash", "type", "site_name", "title", "description", "photo", "embed_url", "embed_type", "embed_width", "embed_height", "duration", "author", "document", "cached_page", "attributes"]

    ID = -0x1763ba4e
    QUALNAME = "types.WebPage"

    def __init__(self, *, id: int, url: str, display_url: str, hash: int, type: Optional[str] = None, site_name: Optional[str] = None, title: Optional[str] = None, description: Optional[str] = None, photo: "raw.base.Photo" = None, embed_url: Optional[str] = None, embed_type: Optional[str] = None, embed_width: Optional[int] = None, embed_height: Optional[int] = None, duration: Optional[int] = None, author: Optional[str] = None, document: "raw.base.Document" = None, cached_page: "raw.base.Page" = None, attributes: Optional[List["raw.base.WebPageAttribute"]] = None) -> None:
        self.id = id  # long
        self.url = url  # string
        self.display_url = display_url  # string
        self.hash = hash  # int
        self.type = type  # flags.0?string
        self.site_name = site_name  # flags.1?string
        self.title = title  # flags.2?string
        self.description = description  # flags.3?string
        self.photo = photo  # flags.4?Photo
        self.embed_url = embed_url  # flags.5?string
        self.embed_type = embed_type  # flags.5?string
        self.embed_width = embed_width  # flags.6?int
        self.embed_height = embed_height  # flags.6?int
        self.duration = duration  # flags.7?int
        self.author = author  # flags.8?string
        self.document = document  # flags.9?Document
        self.cached_page = cached_page  # flags.10?Page
        self.attributes = attributes  # flags.12?Vector<WebPageAttribute>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        id = Long.read(data)
        
        url = String.read(data)
        
        display_url = String.read(data)
        
        hash = Int.read(data)
        
        type = String.read(data) if flags & (1 << 0) else None
        site_name = String.read(data) if flags & (1 << 1) else None
        title = String.read(data) if flags & (1 << 2) else None
        description = String.read(data) if flags & (1 << 3) else None
        photo = TLObject.read(data) if flags & (1 << 4) else None
        
        embed_url = String.read(data) if flags & (1 << 5) else None
        embed_type = String.read(data) if flags & (1 << 5) else None
        embed_width = Int.read(data) if flags & (1 << 6) else None
        embed_height = Int.read(data) if flags & (1 << 6) else None
        duration = Int.read(data) if flags & (1 << 7) else None
        author = String.read(data) if flags & (1 << 8) else None
        document = TLObject.read(data) if flags & (1 << 9) else None
        
        cached_page = TLObject.read(data) if flags & (1 << 10) else None
        
        attributes = TLObject.read(data) if flags & (1 << 12) else []
        
        return WebPage(id=id, url=url, display_url=display_url, hash=hash, type=type, site_name=site_name, title=title, description=description, photo=photo, embed_url=embed_url, embed_type=embed_type, embed_width=embed_width, embed_height=embed_height, duration=duration, author=author, document=document, cached_page=cached_page, attributes=attributes)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.type is not None else 0
        flags |= (1 << 1) if self.site_name is not None else 0
        flags |= (1 << 2) if self.title is not None else 0
        flags |= (1 << 3) if self.description is not None else 0
        flags |= (1 << 4) if self.photo is not None else 0
        flags |= (1 << 5) if self.embed_url is not None else 0
        flags |= (1 << 5) if self.embed_type is not None else 0
        flags |= (1 << 6) if self.embed_width is not None else 0
        flags |= (1 << 6) if self.embed_height is not None else 0
        flags |= (1 << 7) if self.duration is not None else 0
        flags |= (1 << 8) if self.author is not None else 0
        flags |= (1 << 9) if self.document is not None else 0
        flags |= (1 << 10) if self.cached_page is not None else 0
        flags |= (1 << 12) if self.attributes is not None else 0
        data.write(Int(flags))
        
        data.write(Long(self.id))
        
        data.write(String(self.url))
        
        data.write(String(self.display_url))
        
        data.write(Int(self.hash))
        
        if self.type is not None:
            data.write(String(self.type))
        
        if self.site_name is not None:
            data.write(String(self.site_name))
        
        if self.title is not None:
            data.write(String(self.title))
        
        if self.description is not None:
            data.write(String(self.description))
        
        if self.photo is not None:
            data.write(self.photo.write())
        
        if self.embed_url is not None:
            data.write(String(self.embed_url))
        
        if self.embed_type is not None:
            data.write(String(self.embed_type))
        
        if self.embed_width is not None:
            data.write(Int(self.embed_width))
        
        if self.embed_height is not None:
            data.write(Int(self.embed_height))
        
        if self.duration is not None:
            data.write(Int(self.duration))
        
        if self.author is not None:
            data.write(String(self.author))
        
        if self.document is not None:
            data.write(self.document.write())
        
        if self.cached_page is not None:
            data.write(self.cached_page.write())
        
        if self.attributes is not None:
            data.write(Vector(self.attributes))
        
        return data.getvalue()

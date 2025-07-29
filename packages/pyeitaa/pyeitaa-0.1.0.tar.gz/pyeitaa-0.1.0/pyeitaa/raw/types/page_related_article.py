from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, String
from pyeitaa.raw.core import TLObject
from typing import List, Optional, Any, Self


class PageRelatedArticle(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.PageRelatedArticle`.

    Details:
        - Layer: ``135``
        - ID: ``-0x4c6f23f8``

    Parameters:
        url: ``str``
        webpage_id: ``int`` ``64-bit``
        title (optional): ``str``
        description (optional): ``str``
        photo_id (optional): ``int`` ``64-bit``
        author (optional): ``str``
        published_date (optional): ``int`` ``32-bit``
    """

    __slots__: List[str] = ["url", "webpage_id", "title", "description", "photo_id", "author", "published_date"]

    ID = -0x4c6f23f8
    QUALNAME = "types.PageRelatedArticle"

    def __init__(self, *, url: str, webpage_id: int, title: Optional[str] = None, description: Optional[str] = None, photo_id: Optional[int] = None, author: Optional[str] = None, published_date: Optional[int] = None) -> None:
        self.url = url  # string
        self.webpage_id = webpage_id  # long
        self.title = title  # flags.0?string
        self.description = description  # flags.1?string
        self.photo_id = photo_id  # flags.2?long
        self.author = author  # flags.3?string
        self.published_date = published_date  # flags.4?int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        url = String.read(data)
        
        webpage_id = Long.read(data)
        
        title = String.read(data) if flags & (1 << 0) else None
        description = String.read(data) if flags & (1 << 1) else None
        photo_id = Long.read(data) if flags & (1 << 2) else None
        author = String.read(data) if flags & (1 << 3) else None
        published_date = Int.read(data) if flags & (1 << 4) else None
        return PageRelatedArticle(url=url, webpage_id=webpage_id, title=title, description=description, photo_id=photo_id, author=author, published_date=published_date)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.title is not None else 0
        flags |= (1 << 1) if self.description is not None else 0
        flags |= (1 << 2) if self.photo_id is not None else 0
        flags |= (1 << 3) if self.author is not None else 0
        flags |= (1 << 4) if self.published_date is not None else 0
        data.write(Int(flags))
        
        data.write(String(self.url))
        
        data.write(Long(self.webpage_id))
        
        if self.title is not None:
            data.write(String(self.title))
        
        if self.description is not None:
            data.write(String(self.description))
        
        if self.photo_id is not None:
            data.write(Long(self.photo_id))
        
        if self.author is not None:
            data.write(String(self.author))
        
        if self.published_date is not None:
            data.write(Int(self.published_date))
        
        return data.getvalue()

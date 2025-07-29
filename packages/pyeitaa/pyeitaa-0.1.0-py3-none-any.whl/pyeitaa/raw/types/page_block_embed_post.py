from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, String, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class PageBlockEmbedPost(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.PageBlock`.

    Details:
        - Layer: ``135``
        - ID: ``-0xda657f5``

    Parameters:
        url: ``str``
        webpage_id: ``int`` ``64-bit``
        author_photo_id: ``int`` ``64-bit``
        author: ``str``
        date: ``int`` ``32-bit``
        blocks: List of :obj:`PageBlock <pyeitaa.raw.base.PageBlock>`
        caption: :obj:`PageCaption <pyeitaa.raw.base.PageCaption>`
    """

    __slots__: List[str] = ["url", "webpage_id", "author_photo_id", "author", "date", "blocks", "caption"]

    ID = -0xda657f5
    QUALNAME = "types.PageBlockEmbedPost"

    def __init__(self, *, url: str, webpage_id: int, author_photo_id: int, author: str, date: int, blocks: List["raw.base.PageBlock"], caption: "raw.base.PageCaption") -> None:
        self.url = url  # string
        self.webpage_id = webpage_id  # long
        self.author_photo_id = author_photo_id  # long
        self.author = author  # string
        self.date = date  # int
        self.blocks = blocks  # Vector<PageBlock>
        self.caption = caption  # PageCaption

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        url = String.read(data)
        
        webpage_id = Long.read(data)
        
        author_photo_id = Long.read(data)
        
        author = String.read(data)
        
        date = Int.read(data)
        
        blocks = TLObject.read(data)
        
        caption = TLObject.read(data)
        
        return PageBlockEmbedPost(url=url, webpage_id=webpage_id, author_photo_id=author_photo_id, author=author, date=date, blocks=blocks, caption=caption)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(String(self.url))
        
        data.write(Long(self.webpage_id))
        
        data.write(Long(self.author_photo_id))
        
        data.write(String(self.author))
        
        data.write(Int(self.date))
        
        data.write(Vector(self.blocks))
        
        data.write(self.caption.write())
        
        return data.getvalue()

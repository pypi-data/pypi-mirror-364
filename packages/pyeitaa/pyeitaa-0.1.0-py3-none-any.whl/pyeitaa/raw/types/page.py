from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class Page(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.Page`.

    Details:
        - Layer: ``135``
        - ID: ``-0x679a80f3``

    Parameters:
        url: ``str``
        blocks: List of :obj:`PageBlock <pyeitaa.raw.base.PageBlock>`
        photos: List of :obj:`Photo <pyeitaa.raw.base.Photo>`
        documents: List of :obj:`Document <pyeitaa.raw.base.Document>`
        part (optional): ``bool``
        rtl (optional): ``bool``
        v2 (optional): ``bool``
        views (optional): ``int`` ``32-bit``
    """

    __slots__: List[str] = ["url", "blocks", "photos", "documents", "part", "rtl", "v2", "views"]

    ID = -0x679a80f3
    QUALNAME = "types.Page"

    def __init__(self, *, url: str, blocks: List["raw.base.PageBlock"], photos: List["raw.base.Photo"], documents: List["raw.base.Document"], part: Optional[bool] = None, rtl: Optional[bool] = None, v2: Optional[bool] = None, views: Optional[int] = None) -> None:
        self.url = url  # string
        self.blocks = blocks  # Vector<PageBlock>
        self.photos = photos  # Vector<Photo>
        self.documents = documents  # Vector<Document>
        self.part = part  # flags.0?true
        self.rtl = rtl  # flags.1?true
        self.v2 = v2  # flags.2?true
        self.views = views  # flags.3?int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        part = True if flags & (1 << 0) else False
        rtl = True if flags & (1 << 1) else False
        v2 = True if flags & (1 << 2) else False
        url = String.read(data)
        
        blocks = TLObject.read(data)
        
        photos = TLObject.read(data)
        
        documents = TLObject.read(data)
        
        views = Int.read(data) if flags & (1 << 3) else None
        return Page(url=url, blocks=blocks, photos=photos, documents=documents, part=part, rtl=rtl, v2=v2, views=views)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.part else 0
        flags |= (1 << 1) if self.rtl else 0
        flags |= (1 << 2) if self.v2 else 0
        flags |= (1 << 3) if self.views is not None else 0
        data.write(Int(flags))
        
        data.write(String(self.url))
        
        data.write(Vector(self.blocks))
        
        data.write(Vector(self.photos))
        
        data.write(Vector(self.documents))
        
        if self.views is not None:
            data.write(Int(self.views))
        
        return data.getvalue()

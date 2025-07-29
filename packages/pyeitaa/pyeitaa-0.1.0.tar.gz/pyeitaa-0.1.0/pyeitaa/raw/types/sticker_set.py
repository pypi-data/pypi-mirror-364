from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, String, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class StickerSet(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.StickerSet`.

    Details:
        - Layer: ``135``
        - ID: ``-0x2820de86``

    Parameters:
        id: ``int`` ``64-bit``
        access_hash: ``int`` ``64-bit``
        title: ``str``
        short_name: ``str``
        count: ``int`` ``32-bit``
        hash: ``int`` ``32-bit``
        archived (optional): ``bool``
        official (optional): ``bool``
        masks (optional): ``bool``
        animated (optional): ``bool``
        installed_date (optional): ``int`` ``32-bit``
        thumbs (optional): List of :obj:`PhotoSize <pyeitaa.raw.base.PhotoSize>`
        thumb_dc_id (optional): ``int`` ``32-bit``
        thumb_version (optional): ``int`` ``32-bit``
    """

    __slots__: List[str] = ["id", "access_hash", "title", "short_name", "count", "hash", "archived", "official", "masks", "animated", "installed_date", "thumbs", "thumb_dc_id", "thumb_version"]

    ID = -0x2820de86
    QUALNAME = "types.StickerSet"

    def __init__(self, *, id: int, access_hash: int, title: str, short_name: str, count: int, hash: int, archived: Optional[bool] = None, official: Optional[bool] = None, masks: Optional[bool] = None, animated: Optional[bool] = None, installed_date: Optional[int] = None, thumbs: Optional[List["raw.base.PhotoSize"]] = None, thumb_dc_id: Optional[int] = None, thumb_version: Optional[int] = None) -> None:
        self.id = id  # long
        self.access_hash = access_hash  # long
        self.title = title  # string
        self.short_name = short_name  # string
        self.count = count  # int
        self.hash = hash  # int
        self.archived = archived  # flags.1?true
        self.official = official  # flags.2?true
        self.masks = masks  # flags.3?true
        self.animated = animated  # flags.5?true
        self.installed_date = installed_date  # flags.0?int
        self.thumbs = thumbs  # flags.4?Vector<PhotoSize>
        self.thumb_dc_id = thumb_dc_id  # flags.4?int
        self.thumb_version = thumb_version  # flags.4?int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        archived = True if flags & (1 << 1) else False
        official = True if flags & (1 << 2) else False
        masks = True if flags & (1 << 3) else False
        animated = True if flags & (1 << 5) else False
        installed_date = Int.read(data) if flags & (1 << 0) else None
        id = Long.read(data)
        
        access_hash = Long.read(data)
        
        title = String.read(data)
        
        short_name = String.read(data)
        
        thumbs = TLObject.read(data) if flags & (1 << 4) else []
        
        thumb_dc_id = Int.read(data) if flags & (1 << 4) else None
        thumb_version = Int.read(data) if flags & (1 << 4) else None
        count = Int.read(data)
        
        hash = Int.read(data)
        
        return StickerSet(id=id, access_hash=access_hash, title=title, short_name=short_name, count=count, hash=hash, archived=archived, official=official, masks=masks, animated=animated, installed_date=installed_date, thumbs=thumbs, thumb_dc_id=thumb_dc_id, thumb_version=thumb_version)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 1) if self.archived else 0
        flags |= (1 << 2) if self.official else 0
        flags |= (1 << 3) if self.masks else 0
        flags |= (1 << 5) if self.animated else 0
        flags |= (1 << 0) if self.installed_date is not None else 0
        flags |= (1 << 4) if self.thumbs is not None else 0
        flags |= (1 << 4) if self.thumb_dc_id is not None else 0
        flags |= (1 << 4) if self.thumb_version is not None else 0
        data.write(Int(flags))
        
        if self.installed_date is not None:
            data.write(Int(self.installed_date))
        
        data.write(Long(self.id))
        
        data.write(Long(self.access_hash))
        
        data.write(String(self.title))
        
        data.write(String(self.short_name))
        
        if self.thumbs is not None:
            data.write(Vector(self.thumbs))
        
        if self.thumb_dc_id is not None:
            data.write(Int(self.thumb_dc_id))
        
        if self.thumb_version is not None:
            data.write(Int(self.thumb_version))
        
        data.write(Int(self.count))
        
        data.write(Int(self.hash))
        
        return data.getvalue()

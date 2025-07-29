from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, Bytes, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class Photo(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.Photo`.

    Details:
        - Layer: ``135``
        - ID: ``-0x4e6859b``

    Parameters:
        id: ``int`` ``64-bit``
        access_hash: ``int`` ``64-bit``
        file_reference: ``bytes``
        date: ``int`` ``32-bit``
        sizes: List of :obj:`PhotoSize <pyeitaa.raw.base.PhotoSize>`
        dc_id: ``int`` ``32-bit``
        has_stickers (optional): ``bool``
        video_sizes (optional): List of :obj:`VideoSize <pyeitaa.raw.base.VideoSize>`
    """

    __slots__: List[str] = ["id", "access_hash", "file_reference", "date", "sizes", "dc_id", "has_stickers", "video_sizes"]

    ID = -0x4e6859b
    QUALNAME = "types.Photo"

    def __init__(self, *, id: int, access_hash: int, file_reference: bytes, date: int, sizes: List["raw.base.PhotoSize"], dc_id: int, has_stickers: Optional[bool] = None, video_sizes: Optional[List["raw.base.VideoSize"]] = None) -> None:
        self.id = id  # long
        self.access_hash = access_hash  # long
        self.file_reference = file_reference  # bytes
        self.date = date  # int
        self.sizes = sizes  # Vector<PhotoSize>
        self.dc_id = dc_id  # int
        self.has_stickers = has_stickers  # flags.0?true
        self.video_sizes = video_sizes  # flags.1?Vector<VideoSize>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        has_stickers = True if flags & (1 << 0) else False
        id = Long.read(data)
        
        access_hash = Long.read(data)
        
        file_reference = Bytes.read(data)
        
        date = Int.read(data)
        
        sizes = TLObject.read(data)
        
        video_sizes = TLObject.read(data) if flags & (1 << 1) else []
        
        dc_id = Int.read(data)
        
        return Photo(id=id, access_hash=access_hash, file_reference=file_reference, date=date, sizes=sizes, dc_id=dc_id, has_stickers=has_stickers, video_sizes=video_sizes)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.has_stickers else 0
        flags |= (1 << 1) if self.video_sizes is not None else 0
        data.write(Int(flags))
        
        data.write(Long(self.id))
        
        data.write(Long(self.access_hash))
        
        data.write(Bytes(self.file_reference))
        
        data.write(Int(self.date))
        
        data.write(Vector(self.sizes))
        
        if self.video_sizes is not None:
            data.write(Vector(self.video_sizes))
        
        data.write(Int(self.dc_id))
        
        return data.getvalue()

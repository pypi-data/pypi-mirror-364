from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, Bytes, String, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class Document(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.Document`.

    Details:
        - Layer: ``135``
        - ID: ``0x1e87342b``

    Parameters:
        id: ``int`` ``64-bit``
        access_hash: ``int`` ``64-bit``
        file_reference: ``bytes``
        date: ``int`` ``32-bit``
        mime_type: ``str``
        size: ``int`` ``32-bit``
        dc_id: ``int`` ``32-bit``
        attributes: List of :obj:`DocumentAttribute <pyeitaa.raw.base.DocumentAttribute>`
        thumbs (optional): List of :obj:`PhotoSize <pyeitaa.raw.base.PhotoSize>`
        video_thumbs (optional): List of :obj:`VideoSize <pyeitaa.raw.base.VideoSize>`

    See Also:
        This object can be returned by 2 methods:

        .. hlist::
            :columns: 2

            - :obj:`account.UploadTheme <pyeitaa.raw.functions.account.UploadTheme>`
            - :obj:`messages.GetDocumentByHash <pyeitaa.raw.functions.messages.GetDocumentByHash>`
    """

    __slots__: List[str] = ["id", "access_hash", "file_reference", "date", "mime_type", "size", "dc_id", "attributes", "thumbs", "video_thumbs"]

    ID = 0x1e87342b
    QUALNAME = "types.Document"

    def __init__(self, *, id: int, access_hash: int, file_reference: bytes, date: int, mime_type: str, size: int, dc_id: int, attributes: List["raw.base.DocumentAttribute"], thumbs: Optional[List["raw.base.PhotoSize"]] = None, video_thumbs: Optional[List["raw.base.VideoSize"]] = None) -> None:
        self.id = id  # long
        self.access_hash = access_hash  # long
        self.file_reference = file_reference  # bytes
        self.date = date  # int
        self.mime_type = mime_type  # string
        self.size = size  # int
        self.dc_id = dc_id  # int
        self.attributes = attributes  # Vector<DocumentAttribute>
        self.thumbs = thumbs  # flags.0?Vector<PhotoSize>
        self.video_thumbs = video_thumbs  # flags.1?Vector<VideoSize>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        id = Long.read(data)
        
        access_hash = Long.read(data)
        
        file_reference = Bytes.read(data)
        
        date = Int.read(data)
        
        mime_type = String.read(data)
        
        size = Int.read(data)
        
        thumbs = TLObject.read(data) if flags & (1 << 0) else []
        
        video_thumbs = TLObject.read(data) if flags & (1 << 1) else []
        
        dc_id = Int.read(data)
        
        attributes = TLObject.read(data)
        
        return Document(id=id, access_hash=access_hash, file_reference=file_reference, date=date, mime_type=mime_type, size=size, dc_id=dc_id, attributes=attributes, thumbs=thumbs, video_thumbs=video_thumbs)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.thumbs is not None else 0
        flags |= (1 << 1) if self.video_thumbs is not None else 0
        data.write(Int(flags))
        
        data.write(Long(self.id))
        
        data.write(Long(self.access_hash))
        
        data.write(Bytes(self.file_reference))
        
        data.write(Int(self.date))
        
        data.write(String(self.mime_type))
        
        data.write(Int(self.size))
        
        if self.thumbs is not None:
            data.write(Vector(self.thumbs))
        
        if self.video_thumbs is not None:
            data.write(Vector(self.video_thumbs))
        
        data.write(Int(self.dc_id))
        
        data.write(Vector(self.attributes))
        
        return data.getvalue()

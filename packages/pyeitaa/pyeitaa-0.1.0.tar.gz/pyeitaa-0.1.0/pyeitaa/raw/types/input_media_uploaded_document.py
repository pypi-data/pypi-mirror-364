from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class InputMediaUploadedDocument(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.InputMedia`.

    Details:
        - Layer: ``135``
        - ID: ``0x5b38c6c1``

    Parameters:
        file: :obj:`InputFile <pyeitaa.raw.base.InputFile>`
        mime_type: ``str``
        attributes: List of :obj:`DocumentAttribute <pyeitaa.raw.base.DocumentAttribute>`
        nosound_video (optional): ``bool``
        force_file (optional): ``bool``
        thumb (optional): :obj:`InputFile <pyeitaa.raw.base.InputFile>`
        stickers (optional): List of :obj:`InputDocument <pyeitaa.raw.base.InputDocument>`
        ttl_seconds (optional): ``int`` ``32-bit``
    """

    __slots__: List[str] = ["file", "mime_type", "attributes", "nosound_video", "force_file", "thumb", "stickers", "ttl_seconds"]

    ID = 0x5b38c6c1
    QUALNAME = "types.InputMediaUploadedDocument"

    def __init__(self, *, file: "raw.base.InputFile", mime_type: str, attributes: List["raw.base.DocumentAttribute"], nosound_video: Optional[bool] = None, force_file: Optional[bool] = None, thumb: "raw.base.InputFile" = None, stickers: Optional[List["raw.base.InputDocument"]] = None, ttl_seconds: Optional[int] = None) -> None:
        self.file = file  # InputFile
        self.mime_type = mime_type  # string
        self.attributes = attributes  # Vector<DocumentAttribute>
        self.nosound_video = nosound_video  # flags.3?true
        self.force_file = force_file  # flags.4?true
        self.thumb = thumb  # flags.2?InputFile
        self.stickers = stickers  # flags.0?Vector<InputDocument>
        self.ttl_seconds = ttl_seconds  # flags.1?int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        nosound_video = True if flags & (1 << 3) else False
        force_file = True if flags & (1 << 4) else False
        file = TLObject.read(data)
        
        thumb = TLObject.read(data) if flags & (1 << 2) else None
        
        mime_type = String.read(data)
        
        attributes = TLObject.read(data)
        
        stickers = TLObject.read(data) if flags & (1 << 0) else []
        
        ttl_seconds = Int.read(data) if flags & (1 << 1) else None
        return InputMediaUploadedDocument(file=file, mime_type=mime_type, attributes=attributes, nosound_video=nosound_video, force_file=force_file, thumb=thumb, stickers=stickers, ttl_seconds=ttl_seconds)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 3) if self.nosound_video else 0
        flags |= (1 << 4) if self.force_file else 0
        flags |= (1 << 2) if self.thumb is not None else 0
        flags |= (1 << 0) if self.stickers is not None else 0
        flags |= (1 << 1) if self.ttl_seconds is not None else 0
        data.write(Int(flags))
        
        data.write(self.file.write())
        
        if self.thumb is not None:
            data.write(self.thumb.write())
        
        data.write(String(self.mime_type))
        
        data.write(Vector(self.attributes))
        
        if self.stickers is not None:
            data.write(Vector(self.stickers))
        
        if self.ttl_seconds is not None:
            data.write(Int(self.ttl_seconds))
        
        return data.getvalue()

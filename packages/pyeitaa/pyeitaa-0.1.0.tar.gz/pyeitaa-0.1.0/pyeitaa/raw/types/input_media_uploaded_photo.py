from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class InputMediaUploadedPhoto(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.InputMedia`.

    Details:
        - Layer: ``135``
        - ID: ``0x1e287d04``

    Parameters:
        file: :obj:`InputFile <pyeitaa.raw.base.InputFile>`
        stickers (optional): List of :obj:`InputDocument <pyeitaa.raw.base.InputDocument>`
        ttl_seconds (optional): ``int`` ``32-bit``
    """

    __slots__: List[str] = ["file", "stickers", "ttl_seconds"]

    ID = 0x1e287d04
    QUALNAME = "types.InputMediaUploadedPhoto"

    def __init__(self, *, file: "raw.base.InputFile", stickers: Optional[List["raw.base.InputDocument"]] = None, ttl_seconds: Optional[int] = None) -> None:
        self.file = file  # InputFile
        self.stickers = stickers  # flags.0?Vector<InputDocument>
        self.ttl_seconds = ttl_seconds  # flags.1?int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        file = TLObject.read(data)
        
        stickers = TLObject.read(data) if flags & (1 << 0) else []
        
        ttl_seconds = Int.read(data) if flags & (1 << 1) else None
        return InputMediaUploadedPhoto(file=file, stickers=stickers, ttl_seconds=ttl_seconds)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.stickers is not None else 0
        flags |= (1 << 1) if self.ttl_seconds is not None else 0
        data.write(Int(flags))
        
        data.write(self.file.write())
        
        if self.stickers is not None:
            data.write(Vector(self.stickers))
        
        if self.ttl_seconds is not None:
            data.write(Int(self.ttl_seconds))
        
        return data.getvalue()

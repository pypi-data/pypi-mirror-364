from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, String
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class Game(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.Game`.

    Details:
        - Layer: ``135``
        - ID: ``-0x42069ac5``

    Parameters:
        id: ``int`` ``64-bit``
        access_hash: ``int`` ``64-bit``
        short_name: ``str``
        title: ``str``
        description: ``str``
        photo: :obj:`Photo <pyeitaa.raw.base.Photo>`
        document (optional): :obj:`Document <pyeitaa.raw.base.Document>`
    """

    __slots__: List[str] = ["id", "access_hash", "short_name", "title", "description", "photo", "document"]

    ID = -0x42069ac5
    QUALNAME = "types.Game"

    def __init__(self, *, id: int, access_hash: int, short_name: str, title: str, description: str, photo: "raw.base.Photo", document: "raw.base.Document" = None) -> None:
        self.id = id  # long
        self.access_hash = access_hash  # long
        self.short_name = short_name  # string
        self.title = title  # string
        self.description = description  # string
        self.photo = photo  # Photo
        self.document = document  # flags.0?Document

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        id = Long.read(data)
        
        access_hash = Long.read(data)
        
        short_name = String.read(data)
        
        title = String.read(data)
        
        description = String.read(data)
        
        photo = TLObject.read(data)
        
        document = TLObject.read(data) if flags & (1 << 0) else None
        
        return Game(id=id, access_hash=access_hash, short_name=short_name, title=title, description=description, photo=photo, document=document)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.document is not None else 0
        data.write(Int(flags))
        
        data.write(Long(self.id))
        
        data.write(Long(self.access_hash))
        
        data.write(String(self.short_name))
        
        data.write(String(self.title))
        
        data.write(String(self.description))
        
        data.write(self.photo.write())
        
        if self.document is not None:
            data.write(self.document.write())
        
        return data.getvalue()

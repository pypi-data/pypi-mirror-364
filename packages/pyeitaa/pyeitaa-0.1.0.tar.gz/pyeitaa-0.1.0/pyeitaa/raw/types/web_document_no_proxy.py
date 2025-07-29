from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class WebDocumentNoProxy(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.WebDocument`.

    Details:
        - Layer: ``135``
        - ID: ``-0x637433a``

    Parameters:
        url: ``str``
        size: ``int`` ``32-bit``
        mime_type: ``str``
        attributes: List of :obj:`DocumentAttribute <pyeitaa.raw.base.DocumentAttribute>`
    """

    __slots__: List[str] = ["url", "size", "mime_type", "attributes"]

    ID = -0x637433a
    QUALNAME = "types.WebDocumentNoProxy"

    def __init__(self, *, url: str, size: int, mime_type: str, attributes: List["raw.base.DocumentAttribute"]) -> None:
        self.url = url  # string
        self.size = size  # int
        self.mime_type = mime_type  # string
        self.attributes = attributes  # Vector<DocumentAttribute>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        url = String.read(data)
        
        size = Int.read(data)
        
        mime_type = String.read(data)
        
        attributes = TLObject.read(data)
        
        return WebDocumentNoProxy(url=url, size=size, mime_type=mime_type, attributes=attributes)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(String(self.url))
        
        data.write(Int(self.size))
        
        data.write(String(self.mime_type))
        
        data.write(Vector(self.attributes))
        
        return data.getvalue()

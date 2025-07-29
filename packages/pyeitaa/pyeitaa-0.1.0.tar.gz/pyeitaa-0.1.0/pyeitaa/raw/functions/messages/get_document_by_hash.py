from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Bytes, String
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class GetDocumentByHash(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x338e2464``

    Parameters:
        sha256: ``bytes``
        size: ``int`` ``32-bit``
        mime_type: ``str``

    Returns:
        :obj:`Document <pyeitaa.raw.base.Document>`
    """

    __slots__: List[str] = ["sha256", "size", "mime_type"]

    ID = 0x338e2464
    QUALNAME = "functions.messages.GetDocumentByHash"

    def __init__(self, *, sha256: bytes, size: int, mime_type: str) -> None:
        self.sha256 = sha256  # bytes
        self.size = size  # int
        self.mime_type = mime_type  # string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        sha256 = Bytes.read(data)
        
        size = Int.read(data)
        
        mime_type = String.read(data)
        
        return GetDocumentByHash(sha256=sha256, size=size, mime_type=mime_type)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Bytes(self.sha256))
        
        data.write(Int(self.size))
        
        data.write(String(self.mime_type))
        
        return data.getvalue()

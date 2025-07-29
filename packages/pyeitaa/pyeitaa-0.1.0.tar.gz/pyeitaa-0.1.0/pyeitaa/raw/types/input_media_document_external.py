from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from typing import List, Optional, Any, Self


class InputMediaDocumentExternal(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.InputMedia`.

    Details:
        - Layer: ``135``
        - ID: ``-0x4ad2367``

    Parameters:
        url: ``str``
        ttl_seconds (optional): ``int`` ``32-bit``
    """

    __slots__: List[str] = ["url", "ttl_seconds"]

    ID = -0x4ad2367
    QUALNAME = "types.InputMediaDocumentExternal"

    def __init__(self, *, url: str, ttl_seconds: Optional[int] = None) -> None:
        self.url = url  # string
        self.ttl_seconds = ttl_seconds  # flags.0?int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        url = String.read(data)
        
        ttl_seconds = Int.read(data) if flags & (1 << 0) else None
        return InputMediaDocumentExternal(url=url, ttl_seconds=ttl_seconds)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.ttl_seconds is not None else 0
        data.write(Int(flags))
        
        data.write(String(self.url))
        
        if self.ttl_seconds is not None:
            data.write(Int(self.ttl_seconds))
        
        return data.getvalue()

from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class InputMediaDocument(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.InputMedia`.

    Details:
        - Layer: ``135``
        - ID: ``0x33473058``

    Parameters:
        id: :obj:`InputDocument <pyeitaa.raw.base.InputDocument>`
        ttl_seconds (optional): ``int`` ``32-bit``
        query (optional): ``str``
    """

    __slots__: List[str] = ["id", "ttl_seconds", "query"]

    ID = 0x33473058
    QUALNAME = "types.InputMediaDocument"

    def __init__(self, *, id: "raw.base.InputDocument", ttl_seconds: Optional[int] = None, query: Optional[str] = None) -> None:
        self.id = id  # InputDocument
        self.ttl_seconds = ttl_seconds  # flags.0?int
        self.query = query  # flags.1?string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        id = TLObject.read(data)
        
        ttl_seconds = Int.read(data) if flags & (1 << 0) else None
        query = String.read(data) if flags & (1 << 1) else None
        return InputMediaDocument(id=id, ttl_seconds=ttl_seconds, query=query)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.ttl_seconds is not None else 0
        flags |= (1 << 1) if self.query is not None else 0
        data.write(Int(flags))
        
        data.write(self.id.write())
        
        if self.ttl_seconds is not None:
            data.write(Int(self.ttl_seconds))
        
        if self.query is not None:
            data.write(String(self.query))
        
        return data.getvalue()

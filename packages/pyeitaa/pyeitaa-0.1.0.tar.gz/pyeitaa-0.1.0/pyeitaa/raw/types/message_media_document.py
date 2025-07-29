from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class MessageMediaDocument(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.MessageMedia`.

    Details:
        - Layer: ``135``
        - ID: ``-0x634f8f29``

    Parameters:
        document (optional): :obj:`Document <pyeitaa.raw.base.Document>`
        ttl_seconds (optional): ``int`` ``32-bit``

    See Also:
        This object can be returned by 3 methods:

        .. hlist::
            :columns: 2

            - :obj:`messages.GetWebPagePreview <pyeitaa.raw.functions.messages.GetWebPagePreview>`
            - :obj:`messages.UploadMedia <pyeitaa.raw.functions.messages.UploadMedia>`
            - :obj:`messages.UploadImportedMedia <pyeitaa.raw.functions.messages.UploadImportedMedia>`
    """

    __slots__: List[str] = ["document", "ttl_seconds"]

    ID = -0x634f8f29
    QUALNAME = "types.MessageMediaDocument"

    def __init__(self, *, document: "raw.base.Document" = None, ttl_seconds: Optional[int] = None) -> None:
        self.document = document  # flags.0?Document
        self.ttl_seconds = ttl_seconds  # flags.2?int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        document = TLObject.read(data) if flags & (1 << 0) else None
        
        ttl_seconds = Int.read(data) if flags & (1 << 2) else None
        return MessageMediaDocument(document=document, ttl_seconds=ttl_seconds)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.document is not None else 0
        flags |= (1 << 2) if self.ttl_seconds is not None else 0
        data.write(Int(flags))
        
        if self.document is not None:
            data.write(self.document.write())
        
        if self.ttl_seconds is not None:
            data.write(Int(self.ttl_seconds))
        
        return data.getvalue()

from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, String
from pyeitaa.raw.core import TLObject
from typing import List, Optional, Any, Self


class SearchStickerSets(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x35705b8a``

    Parameters:
        q: ``str``
        hash: ``int`` ``64-bit``
        exclude_featured (optional): ``bool``

    Returns:
        :obj:`messages.FoundStickerSets <pyeitaa.raw.base.messages.FoundStickerSets>`
    """

    __slots__: List[str] = ["q", "hash", "exclude_featured"]

    ID = 0x35705b8a
    QUALNAME = "functions.messages.SearchStickerSets"

    def __init__(self, *, q: str, hash: int, exclude_featured: Optional[bool] = None) -> None:
        self.q = q  # string
        self.hash = hash  # long
        self.exclude_featured = exclude_featured  # flags.0?true

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        exclude_featured = True if flags & (1 << 0) else False
        q = String.read(data)
        
        hash = Long.read(data)
        
        return SearchStickerSets(q=q, hash=hash, exclude_featured=exclude_featured)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.exclude_featured else 0
        data.write(Int(flags))
        
        data.write(String(self.q))
        
        data.write(Long(self.hash))
        
        return data.getvalue()

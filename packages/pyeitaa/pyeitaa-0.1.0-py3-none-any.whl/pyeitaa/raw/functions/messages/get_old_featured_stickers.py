from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class GetOldFeaturedStickers(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x7ed094a1``

    Parameters:
        offset: ``int`` ``32-bit``
        limit: ``int`` ``32-bit``
        hash: ``int`` ``64-bit``

    Returns:
        :obj:`messages.FeaturedStickers <pyeitaa.raw.base.messages.FeaturedStickers>`
    """

    __slots__: List[str] = ["offset", "limit", "hash"]

    ID = 0x7ed094a1
    QUALNAME = "functions.messages.GetOldFeaturedStickers"

    def __init__(self, *, offset: int, limit: int, hash: int) -> None:
        self.offset = offset  # int
        self.limit = limit  # int
        self.hash = hash  # long

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        offset = Int.read(data)
        
        limit = Int.read(data)
        
        hash = Long.read(data)
        
        return GetOldFeaturedStickers(offset=offset, limit=limit, hash=hash)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Int(self.offset))
        
        data.write(Int(self.limit))
        
        data.write(Long(self.hash))
        
        return data.getvalue()

from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class FeaturedStickers(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.messages.FeaturedStickers`.

    Details:
        - Layer: ``135``
        - ID: ``-0x7b3fdcf0``

    Parameters:
        hash: ``int`` ``64-bit``
        count: ``int`` ``32-bit``
        sets: List of :obj:`StickerSetCovered <pyeitaa.raw.base.StickerSetCovered>`
        unread: List of ``int`` ``64-bit``

    See Also:
        This object can be returned by 2 methods:

        .. hlist::
            :columns: 2

            - :obj:`messages.GetFeaturedStickers <pyeitaa.raw.functions.messages.GetFeaturedStickers>`
            - :obj:`messages.GetOldFeaturedStickers <pyeitaa.raw.functions.messages.GetOldFeaturedStickers>`
    """

    __slots__: List[str] = ["hash", "count", "sets", "unread"]

    ID = -0x7b3fdcf0
    QUALNAME = "types.messages.FeaturedStickers"

    def __init__(self, *, hash: int, count: int, sets: List["raw.base.StickerSetCovered"], unread: List[int]) -> None:
        self.hash = hash  # long
        self.count = count  # int
        self.sets = sets  # Vector<StickerSetCovered>
        self.unread = unread  # Vector<long>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        hash = Long.read(data)
        
        count = Int.read(data)
        
        sets = TLObject.read(data)
        
        unread = TLObject.read(data, Long)
        
        return FeaturedStickers(hash=hash, count=count, sets=sets, unread=unread)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Long(self.hash))
        
        data.write(Int(self.count))
        
        data.write(Vector(self.sets))
        
        data.write(Vector(self.unread, Long))
        
        return data.getvalue()

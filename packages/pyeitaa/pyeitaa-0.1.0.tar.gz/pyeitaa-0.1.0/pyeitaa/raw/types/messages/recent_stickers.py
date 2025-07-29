from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class RecentStickers(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.messages.RecentStickers`.

    Details:
        - Layer: ``135``
        - ID: ``-0x772c83aa``

    Parameters:
        hash: ``int`` ``64-bit``
        packs: List of :obj:`StickerPack <pyeitaa.raw.base.StickerPack>`
        stickers: List of :obj:`Document <pyeitaa.raw.base.Document>`
        dates: List of ``int`` ``32-bit``

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`messages.GetRecentStickers <pyeitaa.raw.functions.messages.GetRecentStickers>`
    """

    __slots__: List[str] = ["hash", "packs", "stickers", "dates"]

    ID = -0x772c83aa
    QUALNAME = "types.messages.RecentStickers"

    def __init__(self, *, hash: int, packs: List["raw.base.StickerPack"], stickers: List["raw.base.Document"], dates: List[int]) -> None:
        self.hash = hash  # long
        self.packs = packs  # Vector<StickerPack>
        self.stickers = stickers  # Vector<Document>
        self.dates = dates  # Vector<int>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        hash = Long.read(data)
        
        packs = TLObject.read(data)
        
        stickers = TLObject.read(data)
        
        dates = TLObject.read(data, Int)
        
        return RecentStickers(hash=hash, packs=packs, stickers=stickers, dates=dates)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Long(self.hash))
        
        data.write(Vector(self.packs))
        
        data.write(Vector(self.stickers))
        
        data.write(Vector(self.dates, Int))
        
        return data.getvalue()

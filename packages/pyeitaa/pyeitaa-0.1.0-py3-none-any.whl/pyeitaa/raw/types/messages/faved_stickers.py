from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class FavedStickers(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.messages.FavedStickers`.

    Details:
        - Layer: ``135``
        - ID: ``0x2cb51097``

    Parameters:
        hash: ``int`` ``64-bit``
        packs: List of :obj:`StickerPack <pyeitaa.raw.base.StickerPack>`
        stickers: List of :obj:`Document <pyeitaa.raw.base.Document>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`messages.GetFavedStickers <pyeitaa.raw.functions.messages.GetFavedStickers>`
    """

    __slots__: List[str] = ["hash", "packs", "stickers"]

    ID = 0x2cb51097
    QUALNAME = "types.messages.FavedStickers"

    def __init__(self, *, hash: int, packs: List["raw.base.StickerPack"], stickers: List["raw.base.Document"]) -> None:
        self.hash = hash  # long
        self.packs = packs  # Vector<StickerPack>
        self.stickers = stickers  # Vector<Document>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        hash = Long.read(data)
        
        packs = TLObject.read(data)
        
        stickers = TLObject.read(data)
        
        return FavedStickers(hash=hash, packs=packs, stickers=stickers)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Long(self.hash))
        
        data.write(Vector(self.packs))
        
        data.write(Vector(self.stickers))
        
        return data.getvalue()

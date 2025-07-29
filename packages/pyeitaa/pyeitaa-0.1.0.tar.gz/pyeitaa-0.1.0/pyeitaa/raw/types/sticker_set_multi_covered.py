from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class StickerSetMultiCovered(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.StickerSetCovered`.

    Details:
        - Layer: ``135``
        - ID: ``0x3407e51b``

    Parameters:
        set: :obj:`StickerSet <pyeitaa.raw.base.StickerSet>`
        covers: List of :obj:`Document <pyeitaa.raw.base.Document>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`messages.GetAttachedStickers <pyeitaa.raw.functions.messages.GetAttachedStickers>`
    """

    __slots__: List[str] = ["set", "covers"]

    ID = 0x3407e51b
    QUALNAME = "types.StickerSetMultiCovered"

    def __init__(self, *, set: "raw.base.StickerSet", covers: List["raw.base.Document"]) -> None:
        self.set = set  # StickerSet
        self.covers = covers  # Vector<Document>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        set = TLObject.read(data)
        
        covers = TLObject.read(data)
        
        return StickerSetMultiCovered(set=set, covers=covers)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.set.write())
        
        data.write(Vector(self.covers))
        
        return data.getvalue()

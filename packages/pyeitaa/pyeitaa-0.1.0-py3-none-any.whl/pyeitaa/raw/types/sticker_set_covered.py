from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class StickerSetCovered(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.StickerSetCovered`.

    Details:
        - Layer: ``135``
        - ID: ``0x6410a5d2``

    Parameters:
        set: :obj:`StickerSet <pyeitaa.raw.base.StickerSet>`
        cover: :obj:`Document <pyeitaa.raw.base.Document>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`messages.GetAttachedStickers <pyeitaa.raw.functions.messages.GetAttachedStickers>`
    """

    __slots__: List[str] = ["set", "cover"]

    ID = 0x6410a5d2
    QUALNAME = "types.StickerSetCovered"

    def __init__(self, *, set: "raw.base.StickerSet", cover: "raw.base.Document") -> None:
        self.set = set  # StickerSet
        self.cover = cover  # Document

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        set = TLObject.read(data)
        
        cover = TLObject.read(data)
        
        return StickerSetCovered(set=set, cover=cover)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.set.write())
        
        data.write(self.cover.write())
        
        return data.getvalue()

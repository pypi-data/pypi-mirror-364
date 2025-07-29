from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class StickerSet(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.messages.StickerSet`.

    Details:
        - Layer: ``135``
        - ID: ``-0x49f5db5a``

    Parameters:
        set: :obj:`StickerSet <pyeitaa.raw.base.StickerSet>`
        packs: List of :obj:`StickerPack <pyeitaa.raw.base.StickerPack>`
        documents: List of :obj:`Document <pyeitaa.raw.base.Document>`

    See Also:
        This object can be returned by 6 methods:

        .. hlist::
            :columns: 2

            - :obj:`messages.GetStickerSet <pyeitaa.raw.functions.messages.GetStickerSet>`
            - :obj:`stickers.CreateStickerSet <pyeitaa.raw.functions.stickers.CreateStickerSet>`
            - :obj:`stickers.RemoveStickerFromSet <pyeitaa.raw.functions.stickers.RemoveStickerFromSet>`
            - :obj:`stickers.ChangeStickerPosition <pyeitaa.raw.functions.stickers.ChangeStickerPosition>`
            - :obj:`stickers.AddStickerToSet <pyeitaa.raw.functions.stickers.AddStickerToSet>`
            - :obj:`stickers.SetStickerSetThumb <pyeitaa.raw.functions.stickers.SetStickerSetThumb>`
    """

    __slots__: List[str] = ["set", "packs", "documents"]

    ID = -0x49f5db5a
    QUALNAME = "types.messages.StickerSet"

    def __init__(self, *, set: "raw.base.StickerSet", packs: List["raw.base.StickerPack"], documents: List["raw.base.Document"]) -> None:
        self.set = set  # StickerSet
        self.packs = packs  # Vector<StickerPack>
        self.documents = documents  # Vector<Document>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        set = TLObject.read(data)
        
        packs = TLObject.read(data)
        
        documents = TLObject.read(data)
        
        return StickerSet(set=set, packs=packs, documents=documents)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.set.write())
        
        data.write(Vector(self.packs))
        
        data.write(Vector(self.documents))
        
        return data.getvalue()

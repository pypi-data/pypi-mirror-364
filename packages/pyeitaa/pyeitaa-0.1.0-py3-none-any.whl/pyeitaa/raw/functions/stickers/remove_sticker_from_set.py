from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class RemoveStickerFromSet(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x889f0af``

    Parameters:
        sticker: :obj:`InputDocument <pyeitaa.raw.base.InputDocument>`

    Returns:
        :obj:`messages.StickerSet <pyeitaa.raw.base.messages.StickerSet>`
    """

    __slots__: List[str] = ["sticker"]

    ID = -0x889f0af
    QUALNAME = "functions.stickers.RemoveStickerFromSet"

    def __init__(self, *, sticker: "raw.base.InputDocument") -> None:
        self.sticker = sticker  # InputDocument

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        sticker = TLObject.read(data)
        
        return RemoveStickerFromSet(sticker=sticker)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.sticker.write())
        
        return data.getvalue()

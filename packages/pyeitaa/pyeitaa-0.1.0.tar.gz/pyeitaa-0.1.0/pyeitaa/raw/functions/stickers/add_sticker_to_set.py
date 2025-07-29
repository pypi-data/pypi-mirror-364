from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class AddStickerToSet(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x79ac0142``

    Parameters:
        stickerset: :obj:`InputStickerSet <pyeitaa.raw.base.InputStickerSet>`
        sticker: :obj:`InputStickerSetItem <pyeitaa.raw.base.InputStickerSetItem>`

    Returns:
        :obj:`messages.StickerSet <pyeitaa.raw.base.messages.StickerSet>`
    """

    __slots__: List[str] = ["stickerset", "sticker"]

    ID = -0x79ac0142
    QUALNAME = "functions.stickers.AddStickerToSet"

    def __init__(self, *, stickerset: "raw.base.InputStickerSet", sticker: "raw.base.InputStickerSetItem") -> None:
        self.stickerset = stickerset  # InputStickerSet
        self.sticker = sticker  # InputStickerSetItem

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        stickerset = TLObject.read(data)
        
        sticker = TLObject.read(data)
        
        return AddStickerToSet(stickerset=stickerset, sticker=sticker)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.stickerset.write())
        
        data.write(self.sticker.write())
        
        return data.getvalue()

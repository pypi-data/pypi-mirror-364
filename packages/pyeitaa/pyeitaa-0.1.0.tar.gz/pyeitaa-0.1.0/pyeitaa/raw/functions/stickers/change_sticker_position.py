from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class ChangeStickerPosition(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x492b36``

    Parameters:
        sticker: :obj:`InputDocument <pyeitaa.raw.base.InputDocument>`
        position: ``int`` ``32-bit``

    Returns:
        :obj:`messages.StickerSet <pyeitaa.raw.base.messages.StickerSet>`
    """

    __slots__: List[str] = ["sticker", "position"]

    ID = -0x492b36
    QUALNAME = "functions.stickers.ChangeStickerPosition"

    def __init__(self, *, sticker: "raw.base.InputDocument", position: int) -> None:
        self.sticker = sticker  # InputDocument
        self.position = position  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        sticker = TLObject.read(data)
        
        position = Int.read(data)
        
        return ChangeStickerPosition(sticker=sticker, position=position)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.sticker.write())
        
        data.write(Int(self.position))
        
        return data.getvalue()

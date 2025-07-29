from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class SetStickerSetThumb(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x65c9b1d0``

    Parameters:
        stickerset: :obj:`InputStickerSet <pyeitaa.raw.base.InputStickerSet>`
        thumb: :obj:`InputDocument <pyeitaa.raw.base.InputDocument>`

    Returns:
        :obj:`messages.StickerSet <pyeitaa.raw.base.messages.StickerSet>`
    """

    __slots__: List[str] = ["stickerset", "thumb"]

    ID = -0x65c9b1d0
    QUALNAME = "functions.stickers.SetStickerSetThumb"

    def __init__(self, *, stickerset: "raw.base.InputStickerSet", thumb: "raw.base.InputDocument") -> None:
        self.stickerset = stickerset  # InputStickerSet
        self.thumb = thumb  # InputDocument

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        stickerset = TLObject.read(data)
        
        thumb = TLObject.read(data)
        
        return SetStickerSetThumb(stickerset=stickerset, thumb=thumb)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.stickerset.write())
        
        data.write(self.thumb.write())
        
        return data.getvalue()

from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class GetStickerSet(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x2619a90e``

    Parameters:
        stickerset: :obj:`InputStickerSet <pyeitaa.raw.base.InputStickerSet>`

    Returns:
        :obj:`messages.StickerSet <pyeitaa.raw.base.messages.StickerSet>`
    """

    __slots__: List[str] = ["stickerset"]

    ID = 0x2619a90e
    QUALNAME = "functions.messages.GetStickerSet"

    def __init__(self, *, stickerset: "raw.base.InputStickerSet") -> None:
        self.stickerset = stickerset  # InputStickerSet

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        stickerset = TLObject.read(data)
        
        return GetStickerSet(stickerset=stickerset)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.stickerset.write())
        
        return data.getvalue()

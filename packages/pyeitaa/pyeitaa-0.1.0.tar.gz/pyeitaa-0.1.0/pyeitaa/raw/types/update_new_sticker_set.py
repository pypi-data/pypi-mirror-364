from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class UpdateNewStickerSet(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.Update`.

    Details:
        - Layer: ``135``
        - ID: ``0x688a30aa``

    Parameters:
        stickerset: :obj:`messages.StickerSet <pyeitaa.raw.base.messages.StickerSet>`
    """

    __slots__: List[str] = ["stickerset"]

    ID = 0x688a30aa
    QUALNAME = "types.UpdateNewStickerSet"

    def __init__(self, *, stickerset: "raw.base.messages.StickerSet") -> None:
        self.stickerset = stickerset  # messages.StickerSet

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        stickerset = TLObject.read(data)
        
        return UpdateNewStickerSet(stickerset=stickerset)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.stickerset.write())
        
        return data.getvalue()

from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class UninstallStickerSet(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x691aa22``

    Parameters:
        stickerset: :obj:`InputStickerSet <pyeitaa.raw.base.InputStickerSet>`

    Returns:
        ``bool``
    """

    __slots__: List[str] = ["stickerset"]

    ID = -0x691aa22
    QUALNAME = "functions.messages.UninstallStickerSet"

    def __init__(self, *, stickerset: "raw.base.InputStickerSet") -> None:
        self.stickerset = stickerset  # InputStickerSet

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        stickerset = TLObject.read(data)
        
        return UninstallStickerSet(stickerset=stickerset)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.stickerset.write())
        
        return data.getvalue()

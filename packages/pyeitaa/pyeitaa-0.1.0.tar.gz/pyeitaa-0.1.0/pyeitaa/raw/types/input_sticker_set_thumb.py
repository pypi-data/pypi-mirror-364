from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class InputStickerSetThumb(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.InputFileLocation`.

    Details:
        - Layer: ``135``
        - ID: ``-0x627b0c25``

    Parameters:
        stickerset: :obj:`InputStickerSet <pyeitaa.raw.base.InputStickerSet>`
        thumb_version: ``int`` ``32-bit``
    """

    __slots__: List[str] = ["stickerset", "thumb_version"]

    ID = -0x627b0c25
    QUALNAME = "types.InputStickerSetThumb"

    def __init__(self, *, stickerset: "raw.base.InputStickerSet", thumb_version: int) -> None:
        self.stickerset = stickerset  # InputStickerSet
        self.thumb_version = thumb_version  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        stickerset = TLObject.read(data)
        
        thumb_version = Int.read(data)
        
        return InputStickerSetThumb(stickerset=stickerset, thumb_version=thumb_version)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.stickerset.write())
        
        data.write(Int(self.thumb_version))
        
        return data.getvalue()

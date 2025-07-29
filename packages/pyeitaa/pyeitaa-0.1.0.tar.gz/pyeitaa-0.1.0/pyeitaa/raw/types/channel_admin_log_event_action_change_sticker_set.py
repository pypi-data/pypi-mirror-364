from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class ChannelAdminLogEventActionChangeStickerSet(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.ChannelAdminLogEventAction`.

    Details:
        - Layer: ``135``
        - ID: ``-0x4e3c3559``

    Parameters:
        prev_stickerset: :obj:`InputStickerSet <pyeitaa.raw.base.InputStickerSet>`
        new_stickerset: :obj:`InputStickerSet <pyeitaa.raw.base.InputStickerSet>`
    """

    __slots__: List[str] = ["prev_stickerset", "new_stickerset"]

    ID = -0x4e3c3559
    QUALNAME = "types.ChannelAdminLogEventActionChangeStickerSet"

    def __init__(self, *, prev_stickerset: "raw.base.InputStickerSet", new_stickerset: "raw.base.InputStickerSet") -> None:
        self.prev_stickerset = prev_stickerset  # InputStickerSet
        self.new_stickerset = new_stickerset  # InputStickerSet

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        prev_stickerset = TLObject.read(data)
        
        new_stickerset = TLObject.read(data)
        
        return ChannelAdminLogEventActionChangeStickerSet(prev_stickerset=prev_stickerset, new_stickerset=new_stickerset)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.prev_stickerset.write())
        
        data.write(self.new_stickerset.write())
        
        return data.getvalue()

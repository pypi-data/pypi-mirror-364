from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class SetStickers(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x15735b07``

    Parameters:
        channel: :obj:`InputChannel <pyeitaa.raw.base.InputChannel>`
        stickerset: :obj:`InputStickerSet <pyeitaa.raw.base.InputStickerSet>`

    Returns:
        ``bool``
    """

    __slots__: List[str] = ["channel", "stickerset"]

    ID = -0x15735b07
    QUALNAME = "functions.channels.SetStickers"

    def __init__(self, *, channel: "raw.base.InputChannel", stickerset: "raw.base.InputStickerSet") -> None:
        self.channel = channel  # InputChannel
        self.stickerset = stickerset  # InputStickerSet

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        channel = TLObject.read(data)
        
        stickerset = TLObject.read(data)
        
        return SetStickers(channel=channel, stickerset=stickerset)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.channel.write())
        
        data.write(self.stickerset.write())
        
        return data.getvalue()

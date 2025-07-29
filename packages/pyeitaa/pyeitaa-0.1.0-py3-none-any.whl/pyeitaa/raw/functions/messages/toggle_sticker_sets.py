from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class ToggleStickerSets(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x4afad016``

    Parameters:
        stickersets: List of :obj:`InputStickerSet <pyeitaa.raw.base.InputStickerSet>`
        uninstall (optional): ``bool``
        archive (optional): ``bool``
        unarchive (optional): ``bool``

    Returns:
        ``bool``
    """

    __slots__: List[str] = ["stickersets", "uninstall", "archive", "unarchive"]

    ID = -0x4afad016
    QUALNAME = "functions.messages.ToggleStickerSets"

    def __init__(self, *, stickersets: List["raw.base.InputStickerSet"], uninstall: Optional[bool] = None, archive: Optional[bool] = None, unarchive: Optional[bool] = None) -> None:
        self.stickersets = stickersets  # Vector<InputStickerSet>
        self.uninstall = uninstall  # flags.0?true
        self.archive = archive  # flags.1?true
        self.unarchive = unarchive  # flags.2?true

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        uninstall = True if flags & (1 << 0) else False
        archive = True if flags & (1 << 1) else False
        unarchive = True if flags & (1 << 2) else False
        stickersets = TLObject.read(data)
        
        return ToggleStickerSets(stickersets=stickersets, uninstall=uninstall, archive=archive, unarchive=unarchive)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.uninstall else 0
        flags |= (1 << 1) if self.archive else 0
        flags |= (1 << 2) if self.unarchive else 0
        data.write(Int(flags))
        
        data.write(Vector(self.stickersets))
        
        return data.getvalue()

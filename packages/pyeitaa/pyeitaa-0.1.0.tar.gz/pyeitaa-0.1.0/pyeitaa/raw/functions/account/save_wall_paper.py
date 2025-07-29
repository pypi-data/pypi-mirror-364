from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Bool
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class SaveWallPaper(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x6c5a5b37``

    Parameters:
        wallpaper: :obj:`InputWallPaper <pyeitaa.raw.base.InputWallPaper>`
        unsave: ``bool``
        settings: :obj:`WallPaperSettings <pyeitaa.raw.base.WallPaperSettings>`

    Returns:
        ``bool``
    """

    __slots__: List[str] = ["wallpaper", "unsave", "settings"]

    ID = 0x6c5a5b37
    QUALNAME = "functions.account.SaveWallPaper"

    def __init__(self, *, wallpaper: "raw.base.InputWallPaper", unsave: bool, settings: "raw.base.WallPaperSettings") -> None:
        self.wallpaper = wallpaper  # InputWallPaper
        self.unsave = unsave  # Bool
        self.settings = settings  # WallPaperSettings

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        wallpaper = TLObject.read(data)
        
        unsave = Bool.read(data)
        
        settings = TLObject.read(data)
        
        return SaveWallPaper(wallpaper=wallpaper, unsave=unsave, settings=settings)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.wallpaper.write())
        
        data.write(Bool(self.unsave))
        
        data.write(self.settings.write())
        
        return data.getvalue()

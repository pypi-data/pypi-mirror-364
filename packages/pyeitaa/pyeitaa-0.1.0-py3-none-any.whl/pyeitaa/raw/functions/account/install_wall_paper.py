from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class InstallWallPaper(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x112a897``

    Parameters:
        wallpaper: :obj:`InputWallPaper <pyeitaa.raw.base.InputWallPaper>`
        settings: :obj:`WallPaperSettings <pyeitaa.raw.base.WallPaperSettings>`

    Returns:
        ``bool``
    """

    __slots__: List[str] = ["wallpaper", "settings"]

    ID = -0x112a897
    QUALNAME = "functions.account.InstallWallPaper"

    def __init__(self, *, wallpaper: "raw.base.InputWallPaper", settings: "raw.base.WallPaperSettings") -> None:
        self.wallpaper = wallpaper  # InputWallPaper
        self.settings = settings  # WallPaperSettings

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        wallpaper = TLObject.read(data)
        
        settings = TLObject.read(data)
        
        return InstallWallPaper(wallpaper=wallpaper, settings=settings)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.wallpaper.write())
        
        data.write(self.settings.write())
        
        return data.getvalue()

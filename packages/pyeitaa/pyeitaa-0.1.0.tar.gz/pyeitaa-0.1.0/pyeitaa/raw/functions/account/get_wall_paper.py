from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class GetWallPaper(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x3722416``

    Parameters:
        wallpaper: :obj:`InputWallPaper <pyeitaa.raw.base.InputWallPaper>`

    Returns:
        :obj:`WallPaper <pyeitaa.raw.base.WallPaper>`
    """

    __slots__: List[str] = ["wallpaper"]

    ID = -0x3722416
    QUALNAME = "functions.account.GetWallPaper"

    def __init__(self, *, wallpaper: "raw.base.InputWallPaper") -> None:
        self.wallpaper = wallpaper  # InputWallPaper

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        wallpaper = TLObject.read(data)
        
        return GetWallPaper(wallpaper=wallpaper)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.wallpaper.write())
        
        return data.getvalue()

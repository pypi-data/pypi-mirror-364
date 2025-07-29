from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class GetMultiWallPapers(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x65ad71dc``

    Parameters:
        wallpapers: List of :obj:`InputWallPaper <pyeitaa.raw.base.InputWallPaper>`

    Returns:
        List of :obj:`WallPaper <pyeitaa.raw.base.WallPaper>`
    """

    __slots__: List[str] = ["wallpapers"]

    ID = 0x65ad71dc
    QUALNAME = "functions.account.GetMultiWallPapers"

    def __init__(self, *, wallpapers: List["raw.base.InputWallPaper"]) -> None:
        self.wallpapers = wallpapers  # Vector<InputWallPaper>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        wallpapers = TLObject.read(data)
        
        return GetMultiWallPapers(wallpapers=wallpapers)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Vector(self.wallpapers))
        
        return data.getvalue()

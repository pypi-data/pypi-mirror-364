from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class WallPapers(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.account.WallPapers`.

    Details:
        - Layer: ``135``
        - ID: ``-0x323c7a74``

    Parameters:
        hash: ``int`` ``64-bit``
        wallpapers: List of :obj:`WallPaper <pyeitaa.raw.base.WallPaper>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`account.GetWallPapers <pyeitaa.raw.functions.account.GetWallPapers>`
    """

    __slots__: List[str] = ["hash", "wallpapers"]

    ID = -0x323c7a74
    QUALNAME = "types.account.WallPapers"

    def __init__(self, *, hash: int, wallpapers: List["raw.base.WallPaper"]) -> None:
        self.hash = hash  # long
        self.wallpapers = wallpapers  # Vector<WallPaper>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        hash = Long.read(data)
        
        wallpapers = TLObject.read(data)
        
        return WallPapers(hash=hash, wallpapers=wallpapers)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Long(self.hash))
        
        data.write(Vector(self.wallpapers))
        
        return data.getvalue()

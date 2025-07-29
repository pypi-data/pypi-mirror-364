from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class WallPaperNoFile(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.WallPaper`.

    Details:
        - Layer: ``135``
        - ID: ``-0x1f7fbeea``

    Parameters:
        id: ``int`` ``64-bit``
        default (optional): ``bool``
        dark (optional): ``bool``
        settings (optional): :obj:`WallPaperSettings <pyeitaa.raw.base.WallPaperSettings>`

    See Also:
        This object can be returned by 3 methods:

        .. hlist::
            :columns: 2

            - :obj:`account.GetWallPaper <pyeitaa.raw.functions.account.GetWallPaper>`
            - :obj:`account.UploadWallPaper <pyeitaa.raw.functions.account.UploadWallPaper>`
            - :obj:`account.GetMultiWallPapers <pyeitaa.raw.functions.account.GetMultiWallPapers>`
    """

    __slots__: List[str] = ["id", "default", "dark", "settings"]

    ID = -0x1f7fbeea
    QUALNAME = "types.WallPaperNoFile"

    def __init__(self, *, id: int, default: Optional[bool] = None, dark: Optional[bool] = None, settings: "raw.base.WallPaperSettings" = None) -> None:
        self.id = id  # long
        self.default = default  # flags.1?true
        self.dark = dark  # flags.4?true
        self.settings = settings  # flags.2?WallPaperSettings

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        
        id = Long.read(data)
        flags = Int.read(data)
        
        default = True if flags & (1 << 1) else False
        dark = True if flags & (1 << 4) else False
        settings = TLObject.read(data) if flags & (1 << 2) else None
        
        return WallPaperNoFile(id=id, default=default, dark=dark, settings=settings)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        
        data.write(Long(self.id))
        flags = 0
        flags |= (1 << 1) if self.default else 0
        flags |= (1 << 4) if self.dark else 0
        flags |= (1 << 2) if self.settings is not None else 0
        data.write(Int(flags))
        
        if self.settings is not None:
            data.write(self.settings.write())
        
        return data.getvalue()

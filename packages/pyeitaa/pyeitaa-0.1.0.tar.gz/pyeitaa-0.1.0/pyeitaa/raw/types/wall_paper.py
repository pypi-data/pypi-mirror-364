from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, String
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class WallPaper(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.WallPaper`.

    Details:
        - Layer: ``135``
        - ID: ``-0x5bc83c13``

    Parameters:
        id: ``int`` ``64-bit``
        access_hash: ``int`` ``64-bit``
        slug: ``str``
        document: :obj:`Document <pyeitaa.raw.base.Document>`
        creator (optional): ``bool``
        default (optional): ``bool``
        pattern (optional): ``bool``
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

    __slots__: List[str] = ["id", "access_hash", "slug", "document", "creator", "default", "pattern", "dark", "settings"]

    ID = -0x5bc83c13
    QUALNAME = "types.WallPaper"

    def __init__(self, *, id: int, access_hash: int, slug: str, document: "raw.base.Document", creator: Optional[bool] = None, default: Optional[bool] = None, pattern: Optional[bool] = None, dark: Optional[bool] = None, settings: "raw.base.WallPaperSettings" = None) -> None:
        self.id = id  # long
        self.access_hash = access_hash  # long
        self.slug = slug  # string
        self.document = document  # Document
        self.creator = creator  # flags.0?true
        self.default = default  # flags.1?true
        self.pattern = pattern  # flags.3?true
        self.dark = dark  # flags.4?true
        self.settings = settings  # flags.2?WallPaperSettings

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        
        id = Long.read(data)
        flags = Int.read(data)
        
        creator = True if flags & (1 << 0) else False
        default = True if flags & (1 << 1) else False
        pattern = True if flags & (1 << 3) else False
        dark = True if flags & (1 << 4) else False
        access_hash = Long.read(data)
        
        slug = String.read(data)
        
        document = TLObject.read(data)
        
        settings = TLObject.read(data) if flags & (1 << 2) else None
        
        return WallPaper(id=id, access_hash=access_hash, slug=slug, document=document, creator=creator, default=default, pattern=pattern, dark=dark, settings=settings)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        
        data.write(Long(self.id))
        flags = 0
        flags |= (1 << 0) if self.creator else 0
        flags |= (1 << 1) if self.default else 0
        flags |= (1 << 3) if self.pattern else 0
        flags |= (1 << 4) if self.dark else 0
        flags |= (1 << 2) if self.settings is not None else 0
        data.write(Int(flags))
        
        data.write(Long(self.access_hash))
        
        data.write(String(self.slug))
        
        data.write(self.document.write())
        
        if self.settings is not None:
            data.write(self.settings.write())
        
        return data.getvalue()

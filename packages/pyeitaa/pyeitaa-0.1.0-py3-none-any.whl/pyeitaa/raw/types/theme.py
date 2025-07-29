from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, String
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class Theme(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.Theme`.

    Details:
        - Layer: ``135``
        - ID: ``-0x17fd4724``

    Parameters:
        id: ``int`` ``64-bit``
        access_hash: ``int`` ``64-bit``
        slug: ``str``
        title: ``str``
        creator (optional): ``bool``
        default (optional): ``bool``
        for_chat (optional): ``bool``
        document (optional): :obj:`Document <pyeitaa.raw.base.Document>`
        settings (optional): :obj:`ThemeSettings <pyeitaa.raw.base.ThemeSettings>`
        installs_count (optional): ``int`` ``32-bit``

    See Also:
        This object can be returned by 3 methods:

        .. hlist::
            :columns: 2

            - :obj:`account.CreateTheme <pyeitaa.raw.functions.account.CreateTheme>`
            - :obj:`account.UpdateTheme <pyeitaa.raw.functions.account.UpdateTheme>`
            - :obj:`account.GetTheme <pyeitaa.raw.functions.account.GetTheme>`
    """

    __slots__: List[str] = ["id", "access_hash", "slug", "title", "creator", "default", "for_chat", "document", "settings", "installs_count"]

    ID = -0x17fd4724
    QUALNAME = "types.Theme"

    def __init__(self, *, id: int, access_hash: int, slug: str, title: str, creator: Optional[bool] = None, default: Optional[bool] = None, for_chat: Optional[bool] = None, document: "raw.base.Document" = None, settings: "raw.base.ThemeSettings" = None, installs_count: Optional[int] = None) -> None:
        self.id = id  # long
        self.access_hash = access_hash  # long
        self.slug = slug  # string
        self.title = title  # string
        self.creator = creator  # flags.0?true
        self.default = default  # flags.1?true
        self.for_chat = for_chat  # flags.5?true
        self.document = document  # flags.2?Document
        self.settings = settings  # flags.3?ThemeSettings
        self.installs_count = installs_count  # flags.4?int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        creator = True if flags & (1 << 0) else False
        default = True if flags & (1 << 1) else False
        for_chat = True if flags & (1 << 5) else False
        id = Long.read(data)
        
        access_hash = Long.read(data)
        
        slug = String.read(data)
        
        title = String.read(data)
        
        document = TLObject.read(data) if flags & (1 << 2) else None
        
        settings = TLObject.read(data) if flags & (1 << 3) else None
        
        installs_count = Int.read(data) if flags & (1 << 4) else None
        return Theme(id=id, access_hash=access_hash, slug=slug, title=title, creator=creator, default=default, for_chat=for_chat, document=document, settings=settings, installs_count=installs_count)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.creator else 0
        flags |= (1 << 1) if self.default else 0
        flags |= (1 << 5) if self.for_chat else 0
        flags |= (1 << 2) if self.document is not None else 0
        flags |= (1 << 3) if self.settings is not None else 0
        flags |= (1 << 4) if self.installs_count is not None else 0
        data.write(Int(flags))
        
        data.write(Long(self.id))
        
        data.write(Long(self.access_hash))
        
        data.write(String(self.slug))
        
        data.write(String(self.title))
        
        if self.document is not None:
            data.write(self.document.write())
        
        if self.settings is not None:
            data.write(self.settings.write())
        
        if self.installs_count is not None:
            data.write(Int(self.installs_count))
        
        return data.getvalue()

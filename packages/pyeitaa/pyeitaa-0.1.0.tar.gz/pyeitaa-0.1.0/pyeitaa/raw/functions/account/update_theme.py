from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class UpdateTheme(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x5cb367d5``

    Parameters:
        format: ``str``
        theme: :obj:`InputTheme <pyeitaa.raw.base.InputTheme>`
        slug (optional): ``str``
        title (optional): ``str``
        document (optional): :obj:`InputDocument <pyeitaa.raw.base.InputDocument>`
        settings (optional): :obj:`InputThemeSettings <pyeitaa.raw.base.InputThemeSettings>`

    Returns:
        :obj:`Theme <pyeitaa.raw.base.Theme>`
    """

    __slots__: List[str] = ["format", "theme", "slug", "title", "document", "settings"]

    ID = 0x5cb367d5
    QUALNAME = "functions.account.UpdateTheme"

    def __init__(self, *, format: str, theme: "raw.base.InputTheme", slug: Optional[str] = None, title: Optional[str] = None, document: "raw.base.InputDocument" = None, settings: "raw.base.InputThemeSettings" = None) -> None:
        self.format = format  # string
        self.theme = theme  # InputTheme
        self.slug = slug  # flags.0?string
        self.title = title  # flags.1?string
        self.document = document  # flags.2?InputDocument
        self.settings = settings  # flags.3?InputThemeSettings

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        format = String.read(data)
        
        theme = TLObject.read(data)
        
        slug = String.read(data) if flags & (1 << 0) else None
        title = String.read(data) if flags & (1 << 1) else None
        document = TLObject.read(data) if flags & (1 << 2) else None
        
        settings = TLObject.read(data) if flags & (1 << 3) else None
        
        return UpdateTheme(format=format, theme=theme, slug=slug, title=title, document=document, settings=settings)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.slug is not None else 0
        flags |= (1 << 1) if self.title is not None else 0
        flags |= (1 << 2) if self.document is not None else 0
        flags |= (1 << 3) if self.settings is not None else 0
        data.write(Int(flags))
        
        data.write(String(self.format))
        
        data.write(self.theme.write())
        
        if self.slug is not None:
            data.write(String(self.slug))
        
        if self.title is not None:
            data.write(String(self.title))
        
        if self.document is not None:
            data.write(self.document.write())
        
        if self.settings is not None:
            data.write(self.settings.write())
        
        return data.getvalue()

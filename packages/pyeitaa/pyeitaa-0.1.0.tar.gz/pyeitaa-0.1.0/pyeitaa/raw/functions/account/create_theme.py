from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class CreateTheme(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x7bcd3de1``

    Parameters:
        slug: ``str``
        title: ``str``
        document (optional): :obj:`InputDocument <pyeitaa.raw.base.InputDocument>`
        settings (optional): :obj:`InputThemeSettings <pyeitaa.raw.base.InputThemeSettings>`

    Returns:
        :obj:`Theme <pyeitaa.raw.base.Theme>`
    """

    __slots__: List[str] = ["slug", "title", "document", "settings"]

    ID = -0x7bcd3de1
    QUALNAME = "functions.account.CreateTheme"

    def __init__(self, *, slug: str, title: str, document: "raw.base.InputDocument" = None, settings: "raw.base.InputThemeSettings" = None) -> None:
        self.slug = slug  # string
        self.title = title  # string
        self.document = document  # flags.2?InputDocument
        self.settings = settings  # flags.3?InputThemeSettings

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        slug = String.read(data)
        
        title = String.read(data)
        
        document = TLObject.read(data) if flags & (1 << 2) else None
        
        settings = TLObject.read(data) if flags & (1 << 3) else None
        
        return CreateTheme(slug=slug, title=title, document=document, settings=settings)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 2) if self.document is not None else 0
        flags |= (1 << 3) if self.settings is not None else 0
        data.write(Int(flags))
        
        data.write(String(self.slug))
        
        data.write(String(self.title))
        
        if self.document is not None:
            data.write(self.document.write())
        
        if self.settings is not None:
            data.write(self.settings.write())
        
        return data.getvalue()

from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class WebPageAttributeTheme(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.WebPageAttribute`.

    Details:
        - Layer: ``135``
        - ID: ``0x54b56617``

    Parameters:
        documents (optional): List of :obj:`Document <pyeitaa.raw.base.Document>`
        settings (optional): :obj:`ThemeSettings <pyeitaa.raw.base.ThemeSettings>`
    """

    __slots__: List[str] = ["documents", "settings"]

    ID = 0x54b56617
    QUALNAME = "types.WebPageAttributeTheme"

    def __init__(self, *, documents: Optional[List["raw.base.Document"]] = None, settings: "raw.base.ThemeSettings" = None) -> None:
        self.documents = documents  # flags.0?Vector<Document>
        self.settings = settings  # flags.1?ThemeSettings

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        documents = TLObject.read(data) if flags & (1 << 0) else []
        
        settings = TLObject.read(data) if flags & (1 << 1) else None
        
        return WebPageAttributeTheme(documents=documents, settings=settings)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.documents is not None else 0
        flags |= (1 << 1) if self.settings is not None else 0
        data.write(Int(flags))
        
        if self.documents is not None:
            data.write(Vector(self.documents))
        
        if self.settings is not None:
            data.write(self.settings.write())
        
        return data.getvalue()

from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class InstallTheme(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x7ae43737``

    Parameters:
        dark (optional): ``bool``
        format (optional): ``str``
        theme (optional): :obj:`InputTheme <pyeitaa.raw.base.InputTheme>`

    Returns:
        ``bool``
    """

    __slots__: List[str] = ["dark", "format", "theme"]

    ID = 0x7ae43737
    QUALNAME = "functions.account.InstallTheme"

    def __init__(self, *, dark: Optional[bool] = None, format: Optional[str] = None, theme: "raw.base.InputTheme" = None) -> None:
        self.dark = dark  # flags.0?true
        self.format = format  # flags.1?string
        self.theme = theme  # flags.1?InputTheme

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        dark = True if flags & (1 << 0) else False
        format = String.read(data) if flags & (1 << 1) else None
        theme = TLObject.read(data) if flags & (1 << 1) else None
        
        return InstallTheme(dark=dark, format=format, theme=theme)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.dark else 0
        flags |= (1 << 1) if self.format is not None else 0
        flags |= (1 << 1) if self.theme is not None else 0
        data.write(Int(flags))
        
        if self.format is not None:
            data.write(String(self.format))
        
        if self.theme is not None:
            data.write(self.theme.write())
        
        return data.getvalue()

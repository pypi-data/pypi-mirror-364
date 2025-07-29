from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class InputThemeSettings(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.InputThemeSettings`.

    Details:
        - Layer: ``135``
        - ID: ``-0x7021afb1``

    Parameters:
        base_theme: :obj:`BaseTheme <pyeitaa.raw.base.BaseTheme>`
        accent_color: ``int`` ``32-bit``
        message_colors_animated (optional): ``bool``
        outbox_accent_color (optional): ``int`` ``32-bit``
        message_colors (optional): List of ``int`` ``32-bit``
        wallpaper (optional): :obj:`InputWallPaper <pyeitaa.raw.base.InputWallPaper>`
        wallpaper_settings (optional): :obj:`WallPaperSettings <pyeitaa.raw.base.WallPaperSettings>`
    """

    __slots__: List[str] = ["base_theme", "accent_color", "message_colors_animated", "outbox_accent_color", "message_colors", "wallpaper", "wallpaper_settings"]

    ID = -0x7021afb1
    QUALNAME = "types.InputThemeSettings"

    def __init__(self, *, base_theme: "raw.base.BaseTheme", accent_color: int, message_colors_animated: Optional[bool] = None, outbox_accent_color: Optional[int] = None, message_colors: Optional[List[int]] = None, wallpaper: "raw.base.InputWallPaper" = None, wallpaper_settings: "raw.base.WallPaperSettings" = None) -> None:
        self.base_theme = base_theme  # BaseTheme
        self.accent_color = accent_color  # int
        self.message_colors_animated = message_colors_animated  # flags.2?true
        self.outbox_accent_color = outbox_accent_color  # flags.3?int
        self.message_colors = message_colors  # flags.0?Vector<int>
        self.wallpaper = wallpaper  # flags.1?InputWallPaper
        self.wallpaper_settings = wallpaper_settings  # flags.1?WallPaperSettings

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        message_colors_animated = True if flags & (1 << 2) else False
        base_theme = TLObject.read(data)
        
        accent_color = Int.read(data)
        
        outbox_accent_color = Int.read(data) if flags & (1 << 3) else None
        message_colors = TLObject.read(data, Int) if flags & (1 << 0) else []
        
        wallpaper = TLObject.read(data) if flags & (1 << 1) else None
        
        wallpaper_settings = TLObject.read(data) if flags & (1 << 1) else None
        
        return InputThemeSettings(base_theme=base_theme, accent_color=accent_color, message_colors_animated=message_colors_animated, outbox_accent_color=outbox_accent_color, message_colors=message_colors, wallpaper=wallpaper, wallpaper_settings=wallpaper_settings)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 2) if self.message_colors_animated else 0
        flags |= (1 << 3) if self.outbox_accent_color is not None else 0
        flags |= (1 << 0) if self.message_colors is not None else 0
        flags |= (1 << 1) if self.wallpaper is not None else 0
        flags |= (1 << 1) if self.wallpaper_settings is not None else 0
        data.write(Int(flags))
        
        data.write(self.base_theme.write())
        
        data.write(Int(self.accent_color))
        
        if self.outbox_accent_color is not None:
            data.write(Int(self.outbox_accent_color))
        
        if self.message_colors is not None:
            data.write(Vector(self.message_colors, Int))
        
        if self.wallpaper is not None:
            data.write(self.wallpaper.write())
        
        if self.wallpaper_settings is not None:
            data.write(self.wallpaper_settings.write())
        
        return data.getvalue()

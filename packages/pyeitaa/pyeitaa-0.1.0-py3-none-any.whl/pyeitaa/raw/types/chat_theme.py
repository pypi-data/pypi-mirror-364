from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class ChatTheme(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.ChatTheme`.

    Details:
        - Layer: ``135``
        - ID: ``-0x12f4a3cd``

    Parameters:
        emoticon: ``str``
        theme: :obj:`Theme <pyeitaa.raw.base.Theme>`
        dark_theme: :obj:`Theme <pyeitaa.raw.base.Theme>`
    """

    __slots__: List[str] = ["emoticon", "theme", "dark_theme"]

    ID = -0x12f4a3cd
    QUALNAME = "types.ChatTheme"

    def __init__(self, *, emoticon: str, theme: "raw.base.Theme", dark_theme: "raw.base.Theme") -> None:
        self.emoticon = emoticon  # string
        self.theme = theme  # Theme
        self.dark_theme = dark_theme  # Theme

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        emoticon = String.read(data)
        
        theme = TLObject.read(data)
        
        dark_theme = TLObject.read(data)
        
        return ChatTheme(emoticon=emoticon, theme=theme, dark_theme=dark_theme)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(String(self.emoticon))
        
        data.write(self.theme.write())
        
        data.write(self.dark_theme.write())
        
        return data.getvalue()

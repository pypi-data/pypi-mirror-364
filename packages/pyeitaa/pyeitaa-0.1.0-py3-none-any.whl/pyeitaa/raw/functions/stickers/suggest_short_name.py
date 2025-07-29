from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class SuggestShortName(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x4dafc503``

    Parameters:
        title: ``str``

    Returns:
        :obj:`stickers.SuggestedShortName <pyeitaa.raw.base.stickers.SuggestedShortName>`
    """

    __slots__: List[str] = ["title"]

    ID = 0x4dafc503
    QUALNAME = "functions.stickers.SuggestShortName"

    def __init__(self, *, title: str) -> None:
        self.title = title  # string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        title = String.read(data)
        
        return SuggestShortName(title=title)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(String(self.title))
        
        return data.getvalue()

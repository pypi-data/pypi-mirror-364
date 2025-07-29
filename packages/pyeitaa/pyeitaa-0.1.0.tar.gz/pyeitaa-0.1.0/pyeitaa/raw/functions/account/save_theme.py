from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Bool
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class SaveTheme(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0xda8ef94``

    Parameters:
        theme: :obj:`InputTheme <pyeitaa.raw.base.InputTheme>`
        unsave: ``bool``

    Returns:
        ``bool``
    """

    __slots__: List[str] = ["theme", "unsave"]

    ID = -0xda8ef94
    QUALNAME = "functions.account.SaveTheme"

    def __init__(self, *, theme: "raw.base.InputTheme", unsave: bool) -> None:
        self.theme = theme  # InputTheme
        self.unsave = unsave  # Bool

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        theme = TLObject.read(data)
        
        unsave = Bool.read(data)
        
        return SaveTheme(theme=theme, unsave=unsave)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.theme.write())
        
        data.write(Bool(self.unsave))
        
        return data.getvalue()

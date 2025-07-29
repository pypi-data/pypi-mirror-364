from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class UpdateTheme(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.Update`.

    Details:
        - Layer: ``135``
        - ID: ``-0x7de9045d``

    Parameters:
        theme: :obj:`Theme <pyeitaa.raw.base.Theme>`
    """

    __slots__: List[str] = ["theme"]

    ID = -0x7de9045d
    QUALNAME = "types.UpdateTheme"

    def __init__(self, *, theme: "raw.base.Theme") -> None:
        self.theme = theme  # Theme

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        theme = TLObject.read(data)
        
        return UpdateTheme(theme=theme)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.theme.write())
        
        return data.getvalue()

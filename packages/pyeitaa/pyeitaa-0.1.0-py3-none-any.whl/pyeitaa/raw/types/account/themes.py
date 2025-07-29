from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class Themes(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.account.Themes`.

    Details:
        - Layer: ``135``
        - ID: ``-0x65c27393``

    Parameters:
        hash: ``int`` ``64-bit``
        themes: List of :obj:`Theme <pyeitaa.raw.base.Theme>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`account.GetThemes <pyeitaa.raw.functions.account.GetThemes>`
    """

    __slots__: List[str] = ["hash", "themes"]

    ID = -0x65c27393
    QUALNAME = "types.account.Themes"

    def __init__(self, *, hash: int, themes: List["raw.base.Theme"]) -> None:
        self.hash = hash  # long
        self.themes = themes  # Vector<Theme>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        hash = Long.read(data)
        
        themes = TLObject.read(data)
        
        return Themes(hash=hash, themes=themes)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Long(self.hash))
        
        data.write(Vector(self.themes))
        
        return data.getvalue()

from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class ChatThemes(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.account.ChatThemes`.

    Details:
        - Layer: ``135``
        - ID: ``-0x1b34143``

    Parameters:
        hash: ``int`` ``32-bit``
        themes: List of :obj:`ChatTheme <pyeitaa.raw.base.ChatTheme>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`account.GetChatThemes <pyeitaa.raw.functions.account.GetChatThemes>`
    """

    __slots__: List[str] = ["hash", "themes"]

    ID = -0x1b34143
    QUALNAME = "types.account.ChatThemes"

    def __init__(self, *, hash: int, themes: List["raw.base.ChatTheme"]) -> None:
        self.hash = hash  # int
        self.themes = themes  # Vector<ChatTheme>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        hash = Int.read(data)
        
        themes = TLObject.read(data)
        
        return ChatThemes(hash=hash, themes=themes)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Int(self.hash))
        
        data.write(Vector(self.themes))
        
        return data.getvalue()

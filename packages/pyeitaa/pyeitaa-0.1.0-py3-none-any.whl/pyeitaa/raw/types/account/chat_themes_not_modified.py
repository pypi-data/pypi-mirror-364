from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class ChatThemesNotModified(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.account.ChatThemes`.

    Details:
        - Layer: ``135``
        - ID: ``-0x1fee1e3c``

    **No parameters required.**

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`account.GetChatThemes <pyeitaa.raw.functions.account.GetChatThemes>`
    """

    __slots__: List[str] = []

    ID = -0x1fee1e3c
    QUALNAME = "types.account.ChatThemesNotModified"

    def __init__(self) -> None:
        pass

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        return ChatThemesNotModified()

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        return data.getvalue()

from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class ChatOnlines(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.ChatOnlines`.

    Details:
        - Layer: ``135``
        - ID: ``-0xfbe1db0``

    Parameters:
        onlines: ``int`` ``32-bit``

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`messages.GetOnlines <pyeitaa.raw.functions.messages.GetOnlines>`
    """

    __slots__: List[str] = ["onlines"]

    ID = -0xfbe1db0
    QUALNAME = "types.ChatOnlines"

    def __init__(self, *, onlines: int) -> None:
        self.onlines = onlines  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        onlines = Int.read(data)
        
        return ChatOnlines(onlines=onlines)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Int(self.onlines))
        
        return data.getvalue()

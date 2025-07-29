from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class ChatEmpty(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.Chat`.

    Details:
        - Layer: ``135``
        - ID: ``0x29562865``

    Parameters:
        id: ``int`` ``64-bit``
    """

    __slots__: List[str] = ["id"]

    ID = 0x29562865
    QUALNAME = "types.ChatEmpty"

    def __init__(self, *, id: int) -> None:
        self.id = id  # long

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        id = Long.read(data)
        
        return ChatEmpty(id=id)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Long(self.id))
        
        return data.getvalue()

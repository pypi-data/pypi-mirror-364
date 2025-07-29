from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, Vector
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class GetAllChats(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x78a08b42``

    Parameters:
        except_ids: List of ``int`` ``64-bit``

    Returns:
        :obj:`messages.Chats <pyeitaa.raw.base.messages.Chats>`
    """

    __slots__: List[str] = ["except_ids"]

    ID = -0x78a08b42
    QUALNAME = "functions.messages.GetAllChats"

    def __init__(self, *, except_ids: List[int]) -> None:
        self.except_ids = except_ids  # Vector<long>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        except_ids = TLObject.read(data, Long)
        
        return GetAllChats(except_ids=except_ids)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Vector(self.except_ids, Long))
        
        return data.getvalue()

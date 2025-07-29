from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class InputMessageCallbackQuery(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.InputMessage`.

    Details:
        - Layer: ``135``
        - ID: ``-0x5305e582``

    Parameters:
        id: ``int`` ``32-bit``
        query_id: ``int`` ``64-bit``
    """

    __slots__: List[str] = ["id", "query_id"]

    ID = -0x5305e582
    QUALNAME = "types.InputMessageCallbackQuery"

    def __init__(self, *, id: int, query_id: int) -> None:
        self.id = id  # int
        self.query_id = query_id  # long

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        id = Int.read(data)
        
        query_id = Long.read(data)
        
        return InputMessageCallbackQuery(id=id, query_id=query_id)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Int(self.id))
        
        data.write(Long(self.query_id))
        
        return data.getvalue()

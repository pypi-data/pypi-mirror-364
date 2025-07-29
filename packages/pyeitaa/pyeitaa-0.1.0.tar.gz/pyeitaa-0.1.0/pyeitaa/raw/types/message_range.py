from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class MessageRange(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.MessageRange`.

    Details:
        - Layer: ``135``
        - ID: ``0xae30253``

    Parameters:
        min_id: ``int`` ``32-bit``
        max_id: ``int`` ``32-bit``

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`messages.GetSplitRanges <pyeitaa.raw.functions.messages.GetSplitRanges>`
    """

    __slots__: List[str] = ["min_id", "max_id"]

    ID = 0xae30253
    QUALNAME = "types.MessageRange"

    def __init__(self, *, min_id: int, max_id: int) -> None:
        self.min_id = min_id  # int
        self.max_id = max_id  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        min_id = Int.read(data)
        
        max_id = Int.read(data)
        
        return MessageRange(min_id=min_id, max_id=max_id)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Int(self.min_id))
        
        data.write(Int(self.max_id))
        
        return data.getvalue()

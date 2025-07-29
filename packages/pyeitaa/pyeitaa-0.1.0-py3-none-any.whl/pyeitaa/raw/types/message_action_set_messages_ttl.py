from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class MessageActionSetMessagesTTL(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.MessageAction`.

    Details:
        - Layer: ``135``
        - ID: ``-0x55e50403``

    Parameters:
        period: ``int`` ``32-bit``
    """

    __slots__: List[str] = ["period"]

    ID = -0x55e50403
    QUALNAME = "types.MessageActionSetMessagesTTL"

    def __init__(self, *, period: int) -> None:
        self.period = period  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        period = Int.read(data)
        
        return MessageActionSetMessagesTTL(period=period)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Int(self.period))
        
        return data.getvalue()

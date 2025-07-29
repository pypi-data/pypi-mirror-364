from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class ReceivedQueue(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x55a5bb66``

    Parameters:
        max_qts: ``int`` ``32-bit``

    Returns:
        List of ``int`` ``64-bit``
    """

    __slots__: List[str] = ["max_qts"]

    ID = 0x55a5bb66
    QUALNAME = "functions.messages.ReceivedQueue"

    def __init__(self, *, max_qts: int) -> None:
        self.max_qts = max_qts  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        max_qts = Int.read(data)
        
        return ReceivedQueue(max_qts=max_qts)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Int(self.max_qts))
        
        return data.getvalue()

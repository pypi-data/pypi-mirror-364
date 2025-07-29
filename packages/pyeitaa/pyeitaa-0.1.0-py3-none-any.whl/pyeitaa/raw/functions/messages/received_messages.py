from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class ReceivedMessages(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x5a954c0``

    Parameters:
        max_id: ``int`` ``32-bit``

    Returns:
        List of :obj:`ReceivedNotifyMessage <pyeitaa.raw.base.ReceivedNotifyMessage>`
    """

    __slots__: List[str] = ["max_id"]

    ID = 0x5a954c0
    QUALNAME = "functions.messages.ReceivedMessages"

    def __init__(self, *, max_id: int) -> None:
        self.max_id = max_id  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        max_id = Int.read(data)
        
        return ReceivedMessages(max_id=max_id)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Int(self.max_id))
        
        return data.getvalue()

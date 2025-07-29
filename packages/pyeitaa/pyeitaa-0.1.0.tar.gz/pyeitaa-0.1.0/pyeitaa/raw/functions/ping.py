from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class Ping(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x7abe77ec``

    Parameters:
        ping_id: ``int`` ``64-bit``

    Returns:
        :obj:`Pong <pyeitaa.raw.base.Pong>`
    """

    __slots__: List[str] = ["ping_id"]

    ID = 0x7abe77ec
    QUALNAME = "functions.Ping"

    def __init__(self, *, ping_id: int) -> None:
        self.ping_id = ping_id  # long

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        ping_id = Long.read(data)
        
        return Ping(ping_id=ping_id)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Long(self.ping_id))
        
        return data.getvalue()

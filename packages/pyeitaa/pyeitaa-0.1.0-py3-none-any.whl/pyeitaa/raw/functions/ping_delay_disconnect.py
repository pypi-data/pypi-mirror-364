from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class PingDelayDisconnect(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0xcbd8474``

    Parameters:
        ping_id: ``int`` ``64-bit``
        disconnect_delay: ``int`` ``32-bit``

    Returns:
        :obj:`Pong <pyeitaa.raw.base.Pong>`
    """

    __slots__: List[str] = ["ping_id", "disconnect_delay"]

    ID = -0xcbd8474
    QUALNAME = "functions.PingDelayDisconnect"

    def __init__(self, *, ping_id: int, disconnect_delay: int) -> None:
        self.ping_id = ping_id  # long
        self.disconnect_delay = disconnect_delay  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        ping_id = Long.read(data)
        
        disconnect_delay = Int.read(data)
        
        return PingDelayDisconnect(ping_id=ping_id, disconnect_delay=disconnect_delay)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Long(self.ping_id))
        
        data.write(Int(self.disconnect_delay))
        
        return data.getvalue()

from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class Pong(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.Pong`.

    Details:
        - Layer: ``135``
        - ID: ``0x347773c5``

    Parameters:
        msg_id: ``int`` ``64-bit``
        ping_id: ``int`` ``64-bit``

    See Also:
        This object can be returned by 4 methods:

        .. hlist::
            :columns: 2

            - :obj:`Ping <pyeitaa.raw.functions.Ping>`
            - :obj:`PingDelayDisconnect <pyeitaa.raw.functions.PingDelayDisconnect>`
            - :obj:`Ping <pyeitaa.raw.functions.Ping>`
            - :obj:`PingDelayDisconnect <pyeitaa.raw.functions.PingDelayDisconnect>`
    """

    __slots__: List[str] = ["msg_id", "ping_id"]

    ID = 0x347773c5
    QUALNAME = "types.Pong"

    def __init__(self, *, msg_id: int, ping_id: int) -> None:
        self.msg_id = msg_id  # long
        self.ping_id = ping_id  # long

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        msg_id = Long.read(data)
        
        ping_id = Long.read(data)
        
        return Pong(msg_id=msg_id, ping_id=ping_id)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Long(self.msg_id))
        
        data.write(Long(self.ping_id))
        
        return data.getvalue()

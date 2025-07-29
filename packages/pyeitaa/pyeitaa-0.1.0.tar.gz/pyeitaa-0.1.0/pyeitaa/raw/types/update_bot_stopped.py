from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, Bool
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class UpdateBotStopped(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.Update`.

    Details:
        - Layer: ``135``
        - ID: ``-0x3b78f5b7``

    Parameters:
        user_id: ``int`` ``64-bit``
        date: ``int`` ``32-bit``
        stopped: ``bool``
        qts: ``int`` ``32-bit``
    """

    __slots__: List[str] = ["user_id", "date", "stopped", "qts"]

    ID = -0x3b78f5b7
    QUALNAME = "types.UpdateBotStopped"

    def __init__(self, *, user_id: int, date: int, stopped: bool, qts: int) -> None:
        self.user_id = user_id  # long
        self.date = date  # int
        self.stopped = stopped  # Bool
        self.qts = qts  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        user_id = Long.read(data)
        
        date = Int.read(data)
        
        stopped = Bool.read(data)
        
        qts = Int.read(data)
        
        return UpdateBotStopped(user_id=user_id, date=date, stopped=stopped, qts=qts)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Long(self.user_id))
        
        data.write(Int(self.date))
        
        data.write(Bool(self.stopped))
        
        data.write(Int(self.qts))
        
        return data.getvalue()

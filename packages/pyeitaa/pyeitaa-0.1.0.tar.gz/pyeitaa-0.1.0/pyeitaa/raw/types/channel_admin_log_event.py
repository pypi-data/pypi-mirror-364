from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class ChannelAdminLogEvent(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.ChannelAdminLogEvent`.

    Details:
        - Layer: ``135``
        - ID: ``0x1fad68cd``

    Parameters:
        id: ``int`` ``64-bit``
        date: ``int`` ``32-bit``
        user_id: ``int`` ``64-bit``
        action: :obj:`ChannelAdminLogEventAction <pyeitaa.raw.base.ChannelAdminLogEventAction>`
    """

    __slots__: List[str] = ["id", "date", "user_id", "action"]

    ID = 0x1fad68cd
    QUALNAME = "types.ChannelAdminLogEvent"

    def __init__(self, *, id: int, date: int, user_id: int, action: "raw.base.ChannelAdminLogEventAction") -> None:
        self.id = id  # long
        self.date = date  # int
        self.user_id = user_id  # long
        self.action = action  # ChannelAdminLogEventAction

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        id = Long.read(data)
        
        date = Int.read(data)
        
        user_id = Long.read(data)
        
        action = TLObject.read(data)
        
        return ChannelAdminLogEvent(id=id, date=date, user_id=user_id, action=action)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Long(self.id))
        
        data.write(Int(self.date))
        
        data.write(Long(self.user_id))
        
        data.write(self.action.write())
        
        return data.getvalue()

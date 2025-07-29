from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class ChannelAdminLogEventActionToggleSlowMode(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.ChannelAdminLogEventAction`.

    Details:
        - Layer: ``135``
        - ID: ``0x53909779``

    Parameters:
        prev_value: ``int`` ``32-bit``
        new_value: ``int`` ``32-bit``
    """

    __slots__: List[str] = ["prev_value", "new_value"]

    ID = 0x53909779
    QUALNAME = "types.ChannelAdminLogEventActionToggleSlowMode"

    def __init__(self, *, prev_value: int, new_value: int) -> None:
        self.prev_value = prev_value  # int
        self.new_value = new_value  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        prev_value = Int.read(data)
        
        new_value = Int.read(data)
        
        return ChannelAdminLogEventActionToggleSlowMode(prev_value=prev_value, new_value=new_value)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Int(self.prev_value))
        
        data.write(Int(self.new_value))
        
        return data.getvalue()

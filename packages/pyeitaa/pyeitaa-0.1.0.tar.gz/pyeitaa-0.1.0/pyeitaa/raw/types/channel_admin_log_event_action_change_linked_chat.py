from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class ChannelAdminLogEventActionChangeLinkedChat(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.ChannelAdminLogEventAction`.

    Details:
        - Layer: ``135``
        - ID: ``0x50c7ac8``

    Parameters:
        prev_value: ``int`` ``64-bit``
        new_value: ``int`` ``64-bit``
    """

    __slots__: List[str] = ["prev_value", "new_value"]

    ID = 0x50c7ac8
    QUALNAME = "types.ChannelAdminLogEventActionChangeLinkedChat"

    def __init__(self, *, prev_value: int, new_value: int) -> None:
        self.prev_value = prev_value  # long
        self.new_value = new_value  # long

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        prev_value = Long.read(data)
        
        new_value = Long.read(data)
        
        return ChannelAdminLogEventActionChangeLinkedChat(prev_value=prev_value, new_value=new_value)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Long(self.prev_value))
        
        data.write(Long(self.new_value))
        
        return data.getvalue()

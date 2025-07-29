from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class ChannelAdminLogEventActionChangeTheme(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.ChannelAdminLogEventAction`.

    Details:
        - Layer: ``135``
        - ID: ``-0x196fe73``

    Parameters:
        prev_value: ``str``
        new_value: ``str``
    """

    __slots__: List[str] = ["prev_value", "new_value"]

    ID = -0x196fe73
    QUALNAME = "types.ChannelAdminLogEventActionChangeTheme"

    def __init__(self, *, prev_value: str, new_value: str) -> None:
        self.prev_value = prev_value  # string
        self.new_value = new_value  # string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        prev_value = String.read(data)
        
        new_value = String.read(data)
        
        return ChannelAdminLogEventActionChangeTheme(prev_value=prev_value, new_value=new_value)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(String(self.prev_value))
        
        data.write(String(self.new_value))
        
        return data.getvalue()

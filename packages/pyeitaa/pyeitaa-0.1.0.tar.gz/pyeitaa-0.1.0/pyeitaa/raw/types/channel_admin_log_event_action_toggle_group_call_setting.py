from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Bool
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class ChannelAdminLogEventActionToggleGroupCallSetting(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.ChannelAdminLogEventAction`.

    Details:
        - Layer: ``135``
        - ID: ``0x56d6a247``

    Parameters:
        join_muted: ``bool``
    """

    __slots__: List[str] = ["join_muted"]

    ID = 0x56d6a247
    QUALNAME = "types.ChannelAdminLogEventActionToggleGroupCallSetting"

    def __init__(self, *, join_muted: bool) -> None:
        self.join_muted = join_muted  # Bool

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        join_muted = Bool.read(data)
        
        return ChannelAdminLogEventActionToggleGroupCallSetting(join_muted=join_muted)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Bool(self.join_muted))
        
        return data.getvalue()

from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class ChannelAdminLogEventActionChangeLocation(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.ChannelAdminLogEventAction`.

    Details:
        - Layer: ``135``
        - ID: ``0xe6b76ae``

    Parameters:
        prev_value: :obj:`ChannelLocation <pyeitaa.raw.base.ChannelLocation>`
        new_value: :obj:`ChannelLocation <pyeitaa.raw.base.ChannelLocation>`
    """

    __slots__: List[str] = ["prev_value", "new_value"]

    ID = 0xe6b76ae
    QUALNAME = "types.ChannelAdminLogEventActionChangeLocation"

    def __init__(self, *, prev_value: "raw.base.ChannelLocation", new_value: "raw.base.ChannelLocation") -> None:
        self.prev_value = prev_value  # ChannelLocation
        self.new_value = new_value  # ChannelLocation

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        prev_value = TLObject.read(data)
        
        new_value = TLObject.read(data)
        
        return ChannelAdminLogEventActionChangeLocation(prev_value=prev_value, new_value=new_value)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.prev_value.write())
        
        data.write(self.new_value.write())
        
        return data.getvalue()

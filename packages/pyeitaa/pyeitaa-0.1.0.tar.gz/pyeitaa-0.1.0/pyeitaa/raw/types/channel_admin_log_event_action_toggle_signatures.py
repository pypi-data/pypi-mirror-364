from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Bool
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class ChannelAdminLogEventActionToggleSignatures(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.ChannelAdminLogEventAction`.

    Details:
        - Layer: ``135``
        - ID: ``0x26ae0971``

    Parameters:
        new_value: ``bool``
    """

    __slots__: List[str] = ["new_value"]

    ID = 0x26ae0971
    QUALNAME = "types.ChannelAdminLogEventActionToggleSignatures"

    def __init__(self, *, new_value: bool) -> None:
        self.new_value = new_value  # Bool

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        new_value = Bool.read(data)
        
        return ChannelAdminLogEventActionToggleSignatures(new_value=new_value)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Bool(self.new_value))
        
        return data.getvalue()

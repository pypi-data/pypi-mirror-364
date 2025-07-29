from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class ChannelAdminLogEventActionDiscardGroupCall(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.ChannelAdminLogEventAction`.

    Details:
        - Layer: ``135``
        - ID: ``-0x24606ec0``

    Parameters:
        call: :obj:`InputGroupCall <pyeitaa.raw.base.InputGroupCall>`
    """

    __slots__: List[str] = ["call"]

    ID = -0x24606ec0
    QUALNAME = "types.ChannelAdminLogEventActionDiscardGroupCall"

    def __init__(self, *, call: "raw.base.InputGroupCall") -> None:
        self.call = call  # InputGroupCall

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        call = TLObject.read(data)
        
        return ChannelAdminLogEventActionDiscardGroupCall(call=call)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.call.write())
        
        return data.getvalue()

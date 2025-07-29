from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class ChannelAdminLogEventActionStopPoll(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.ChannelAdminLogEventAction`.

    Details:
        - Layer: ``135``
        - ID: ``-0x70f869bd``

    Parameters:
        message: :obj:`Message <pyeitaa.raw.base.Message>`
    """

    __slots__: List[str] = ["message"]

    ID = -0x70f869bd
    QUALNAME = "types.ChannelAdminLogEventActionStopPoll"

    def __init__(self, *, message: "raw.base.Message") -> None:
        self.message = message  # Message

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        message = TLObject.read(data)
        
        return ChannelAdminLogEventActionStopPoll(message=message)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.message.write())
        
        return data.getvalue()

from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class ChannelAdminLogEventActionEditMessage(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.ChannelAdminLogEventAction`.

    Details:
        - Layer: ``135``
        - ID: ``0x709b2405``

    Parameters:
        prev_message: :obj:`Message <pyeitaa.raw.base.Message>`
        new_message: :obj:`Message <pyeitaa.raw.base.Message>`
    """

    __slots__: List[str] = ["prev_message", "new_message"]

    ID = 0x709b2405
    QUALNAME = "types.ChannelAdminLogEventActionEditMessage"

    def __init__(self, *, prev_message: "raw.base.Message", new_message: "raw.base.Message") -> None:
        self.prev_message = prev_message  # Message
        self.new_message = new_message  # Message

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        prev_message = TLObject.read(data)
        
        new_message = TLObject.read(data)
        
        return ChannelAdminLogEventActionEditMessage(prev_message=prev_message, new_message=new_message)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.prev_message.write())
        
        data.write(self.new_message.write())
        
        return data.getvalue()

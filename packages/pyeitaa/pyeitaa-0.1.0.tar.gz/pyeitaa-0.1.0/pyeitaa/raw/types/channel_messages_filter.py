from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class ChannelMessagesFilter(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.ChannelMessagesFilter`.

    Details:
        - Layer: ``135``
        - ID: ``-0x328826a9``

    Parameters:
        ranges: List of :obj:`MessageRange <pyeitaa.raw.base.MessageRange>`
        exclude_new_messages (optional): ``bool``
    """

    __slots__: List[str] = ["ranges", "exclude_new_messages"]

    ID = -0x328826a9
    QUALNAME = "types.ChannelMessagesFilter"

    def __init__(self, *, ranges: List["raw.base.MessageRange"], exclude_new_messages: Optional[bool] = None) -> None:
        self.ranges = ranges  # Vector<MessageRange>
        self.exclude_new_messages = exclude_new_messages  # flags.1?true

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        exclude_new_messages = True if flags & (1 << 1) else False
        ranges = TLObject.read(data)
        
        return ChannelMessagesFilter(ranges=ranges, exclude_new_messages=exclude_new_messages)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 1) if self.exclude_new_messages else 0
        data.write(Int(flags))
        
        data.write(Vector(self.ranges))
        
        return data.getvalue()

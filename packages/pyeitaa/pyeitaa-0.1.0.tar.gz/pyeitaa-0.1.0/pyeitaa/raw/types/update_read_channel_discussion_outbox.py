from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class UpdateReadChannelDiscussionOutbox(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.Update`.

    Details:
        - Layer: ``135``
        - ID: ``0x695c9e7c``

    Parameters:
        channel_id: ``int`` ``64-bit``
        top_msg_id: ``int`` ``32-bit``
        read_max_id: ``int`` ``32-bit``
    """

    __slots__: List[str] = ["channel_id", "top_msg_id", "read_max_id"]

    ID = 0x695c9e7c
    QUALNAME = "types.UpdateReadChannelDiscussionOutbox"

    def __init__(self, *, channel_id: int, top_msg_id: int, read_max_id: int) -> None:
        self.channel_id = channel_id  # long
        self.top_msg_id = top_msg_id  # int
        self.read_max_id = read_max_id  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        channel_id = Long.read(data)
        
        top_msg_id = Int.read(data)
        
        read_max_id = Int.read(data)
        
        return UpdateReadChannelDiscussionOutbox(channel_id=channel_id, top_msg_id=top_msg_id, read_max_id=read_max_id)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Long(self.channel_id))
        
        data.write(Int(self.top_msg_id))
        
        data.write(Int(self.read_max_id))
        
        return data.getvalue()

from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, Vector
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class UpdateChannelReadMessagesContents(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.Update`.

    Details:
        - Layer: ``135``
        - ID: ``0x44bdd535``

    Parameters:
        channel_id: ``int`` ``64-bit``
        messages: List of ``int`` ``32-bit``
    """

    __slots__: List[str] = ["channel_id", "messages"]

    ID = 0x44bdd535
    QUALNAME = "types.UpdateChannelReadMessagesContents"

    def __init__(self, *, channel_id: int, messages: List[int]) -> None:
        self.channel_id = channel_id  # long
        self.messages = messages  # Vector<int>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        channel_id = Long.read(data)
        
        messages = TLObject.read(data, Int)
        
        return UpdateChannelReadMessagesContents(channel_id=channel_id, messages=messages)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Long(self.channel_id))
        
        data.write(Vector(self.messages, Int))
        
        return data.getvalue()

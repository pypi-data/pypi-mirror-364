from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class MessageActionChatMigrateTo(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.MessageAction`.

    Details:
        - Layer: ``135``
        - ID: ``-0x1efc806e``

    Parameters:
        channel_id: ``int`` ``64-bit``
    """

    __slots__: List[str] = ["channel_id"]

    ID = -0x1efc806e
    QUALNAME = "types.MessageActionChatMigrateTo"

    def __init__(self, *, channel_id: int) -> None:
        self.channel_id = channel_id  # long

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        channel_id = Long.read(data)
        
        return MessageActionChatMigrateTo(channel_id=channel_id)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Long(self.channel_id))
        
        return data.getvalue()

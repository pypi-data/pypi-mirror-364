from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class GetMessages(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x527365dd``

    Parameters:
        channel: :obj:`InputChannel <pyeitaa.raw.base.InputChannel>`
        id: List of :obj:`InputMessage <pyeitaa.raw.base.InputMessage>`

    Returns:
        :obj:`messages.Messages <pyeitaa.raw.base.messages.Messages>`
    """

    __slots__: List[str] = ["channel", "id"]

    ID = -0x527365dd
    QUALNAME = "functions.channels.GetMessages"

    def __init__(self, *, channel: "raw.base.InputChannel", id: List["raw.base.InputMessage"]) -> None:
        self.channel = channel  # InputChannel
        self.id = id  # Vector<InputMessage>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        channel = TLObject.read(data)
        
        id = TLObject.read(data)
        
        return GetMessages(channel=channel, id=id)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.channel.write())
        
        data.write(Vector(self.id))
        
        return data.getvalue()

from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class DeleteMessages(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x7b3e02b2``

    Parameters:
        channel: :obj:`InputChannel <pyeitaa.raw.base.InputChannel>`
        id: List of ``int`` ``32-bit``

    Returns:
        :obj:`messages.AffectedMessages <pyeitaa.raw.base.messages.AffectedMessages>`
    """

    __slots__: List[str] = ["channel", "id"]

    ID = -0x7b3e02b2
    QUALNAME = "functions.channels.DeleteMessages"

    def __init__(self, *, channel: "raw.base.InputChannel", id: List[int]) -> None:
        self.channel = channel  # InputChannel
        self.id = id  # Vector<int>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        channel = TLObject.read(data)
        
        id = TLObject.read(data, Int)
        
        return DeleteMessages(channel=channel, id=id)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.channel.write())
        
        data.write(Vector(self.id, Int))
        
        return data.getvalue()

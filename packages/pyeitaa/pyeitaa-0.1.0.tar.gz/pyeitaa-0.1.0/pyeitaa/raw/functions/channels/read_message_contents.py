from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class ReadMessageContents(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x154a23c8``

    Parameters:
        channel: :obj:`InputChannel <pyeitaa.raw.base.InputChannel>`
        id: List of ``int`` ``32-bit``

    Returns:
        ``bool``
    """

    __slots__: List[str] = ["channel", "id"]

    ID = -0x154a23c8
    QUALNAME = "functions.channels.ReadMessageContents"

    def __init__(self, *, channel: "raw.base.InputChannel", id: List[int]) -> None:
        self.channel = channel  # InputChannel
        self.id = id  # Vector<int>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        channel = TLObject.read(data)
        
        id = TLObject.read(data, Int)
        
        return ReadMessageContents(channel=channel, id=id)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.channel.write())
        
        data.write(Vector(self.id, Int))
        
        return data.getvalue()

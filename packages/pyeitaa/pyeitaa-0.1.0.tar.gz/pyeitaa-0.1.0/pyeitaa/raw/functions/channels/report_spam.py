from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class ReportSpam(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x1f787f0``

    Parameters:
        channel: :obj:`InputChannel <pyeitaa.raw.base.InputChannel>`
        user_id: :obj:`InputUser <pyeitaa.raw.base.InputUser>`
        id: List of ``int`` ``32-bit``

    Returns:
        ``bool``
    """

    __slots__: List[str] = ["channel", "user_id", "id"]

    ID = -0x1f787f0
    QUALNAME = "functions.channels.ReportSpam"

    def __init__(self, *, channel: "raw.base.InputChannel", user_id: "raw.base.InputUser", id: List[int]) -> None:
        self.channel = channel  # InputChannel
        self.user_id = user_id  # InputUser
        self.id = id  # Vector<int>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        channel = TLObject.read(data)
        
        user_id = TLObject.read(data)
        
        id = TLObject.read(data, Int)
        
        return ReportSpam(channel=channel, user_id=user_id, id=id)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.channel.write())
        
        data.write(self.user_id.write())
        
        data.write(Vector(self.id, Int))
        
        return data.getvalue()

from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class DeleteHistory(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x50c962be``

    Parameters:
        channel: :obj:`InputChannel <pyeitaa.raw.base.InputChannel>`
        max_id: ``int`` ``32-bit``

    Returns:
        ``bool``
    """

    __slots__: List[str] = ["channel", "max_id"]

    ID = -0x50c962be
    QUALNAME = "functions.channels.DeleteHistory"

    def __init__(self, *, channel: "raw.base.InputChannel", max_id: int) -> None:
        self.channel = channel  # InputChannel
        self.max_id = max_id  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        channel = TLObject.read(data)
        
        max_id = Int.read(data)
        
        return DeleteHistory(channel=channel, max_id=max_id)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.channel.write())
        
        data.write(Int(self.max_id))
        
        return data.getvalue()

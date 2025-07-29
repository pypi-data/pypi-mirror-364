from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class UpdateReadChannelOutbox(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.Update`.

    Details:
        - Layer: ``135``
        - ID: ``-0x48a06657``

    Parameters:
        channel_id: ``int`` ``64-bit``
        max_id: ``int`` ``32-bit``
    """

    __slots__: List[str] = ["channel_id", "max_id"]

    ID = -0x48a06657
    QUALNAME = "types.UpdateReadChannelOutbox"

    def __init__(self, *, channel_id: int, max_id: int) -> None:
        self.channel_id = channel_id  # long
        self.max_id = max_id  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        channel_id = Long.read(data)
        
        max_id = Int.read(data)
        
        return UpdateReadChannelOutbox(channel_id=channel_id, max_id=max_id)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Long(self.channel_id))
        
        data.write(Int(self.max_id))
        
        return data.getvalue()

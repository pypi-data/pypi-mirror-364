from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class UpdateChannelAvailableMessages(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.Update`.

    Details:
        - Layer: ``135``
        - ID: ``-0x4dc03968``

    Parameters:
        channel_id: ``int`` ``64-bit``
        available_min_id: ``int`` ``32-bit``
    """

    __slots__: List[str] = ["channel_id", "available_min_id"]

    ID = -0x4dc03968
    QUALNAME = "types.UpdateChannelAvailableMessages"

    def __init__(self, *, channel_id: int, available_min_id: int) -> None:
        self.channel_id = channel_id  # long
        self.available_min_id = available_min_id  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        channel_id = Long.read(data)
        
        available_min_id = Int.read(data)
        
        return UpdateChannelAvailableMessages(channel_id=channel_id, available_min_id=available_min_id)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Long(self.channel_id))
        
        data.write(Int(self.available_min_id))
        
        return data.getvalue()

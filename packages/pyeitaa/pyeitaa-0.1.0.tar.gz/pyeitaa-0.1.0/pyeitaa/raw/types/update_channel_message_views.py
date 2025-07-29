from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class UpdateChannelMessageViews(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.Update`.

    Details:
        - Layer: ``135``
        - ID: ``-0xdd953f8``

    Parameters:
        channel_id: ``int`` ``64-bit``
        id: ``int`` ``32-bit``
        views: ``int`` ``32-bit``
    """

    __slots__: List[str] = ["channel_id", "id", "views"]

    ID = -0xdd953f8
    QUALNAME = "types.UpdateChannelMessageViews"

    def __init__(self, *, channel_id: int, id: int, views: int) -> None:
        self.channel_id = channel_id  # long
        self.id = id  # int
        self.views = views  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        channel_id = Long.read(data)
        
        id = Int.read(data)
        
        views = Int.read(data)
        
        return UpdateChannelMessageViews(channel_id=channel_id, id=id, views=views)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Long(self.channel_id))
        
        data.write(Int(self.id))
        
        data.write(Int(self.views))
        
        return data.getvalue()

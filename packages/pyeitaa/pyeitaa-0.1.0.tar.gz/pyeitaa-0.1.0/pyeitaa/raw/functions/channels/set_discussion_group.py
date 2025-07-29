from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class SetDiscussionGroup(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x40582bb2``

    Parameters:
        broadcast: :obj:`InputChannel <pyeitaa.raw.base.InputChannel>`
        group: :obj:`InputChannel <pyeitaa.raw.base.InputChannel>`

    Returns:
        ``bool``
    """

    __slots__: List[str] = ["broadcast", "group"]

    ID = 0x40582bb2
    QUALNAME = "functions.channels.SetDiscussionGroup"

    def __init__(self, *, broadcast: "raw.base.InputChannel", group: "raw.base.InputChannel") -> None:
        self.broadcast = broadcast  # InputChannel
        self.group = group  # InputChannel

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        broadcast = TLObject.read(data)
        
        group = TLObject.read(data)
        
        return SetDiscussionGroup(broadcast=broadcast, group=group)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.broadcast.write())
        
        data.write(self.group.write())
        
        return data.getvalue()

from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class ToggleSlowMode(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x122b6110``

    Parameters:
        channel: :obj:`InputChannel <pyeitaa.raw.base.InputChannel>`
        seconds: ``int`` ``32-bit``

    Returns:
        :obj:`Updates <pyeitaa.raw.base.Updates>`
    """

    __slots__: List[str] = ["channel", "seconds"]

    ID = -0x122b6110
    QUALNAME = "functions.channels.ToggleSlowMode"

    def __init__(self, *, channel: "raw.base.InputChannel", seconds: int) -> None:
        self.channel = channel  # InputChannel
        self.seconds = seconds  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        channel = TLObject.read(data)
        
        seconds = Int.read(data)
        
        return ToggleSlowMode(channel=channel, seconds=seconds)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.channel.write())
        
        data.write(Int(self.seconds))
        
        return data.getvalue()

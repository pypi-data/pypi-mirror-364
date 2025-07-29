from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Bool
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class ToggleSignatures(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x1f69b606``

    Parameters:
        channel: :obj:`InputChannel <pyeitaa.raw.base.InputChannel>`
        enabled: ``bool``

    Returns:
        :obj:`Updates <pyeitaa.raw.base.Updates>`
    """

    __slots__: List[str] = ["channel", "enabled"]

    ID = 0x1f69b606
    QUALNAME = "functions.channels.ToggleSignatures"

    def __init__(self, *, channel: "raw.base.InputChannel", enabled: bool) -> None:
        self.channel = channel  # InputChannel
        self.enabled = enabled  # Bool

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        channel = TLObject.read(data)
        
        enabled = Bool.read(data)
        
        return ToggleSignatures(channel=channel, enabled=enabled)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.channel.write())
        
        data.write(Bool(self.enabled))
        
        return data.getvalue()

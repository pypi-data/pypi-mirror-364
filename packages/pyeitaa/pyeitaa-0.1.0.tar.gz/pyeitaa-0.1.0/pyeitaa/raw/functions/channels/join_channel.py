from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class JoinChannel(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x24b524c5``

    Parameters:
        channel: :obj:`InputChannel <pyeitaa.raw.base.InputChannel>`

    Returns:
        :obj:`Updates <pyeitaa.raw.base.Updates>`
    """

    __slots__: List[str] = ["channel"]

    ID = 0x24b524c5
    QUALNAME = "functions.channels.JoinChannel"

    def __init__(self, *, channel: "raw.base.InputChannel") -> None:
        self.channel = channel  # InputChannel

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        channel = TLObject.read(data)
        
        return JoinChannel(channel=channel)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.channel.write())
        
        return data.getvalue()

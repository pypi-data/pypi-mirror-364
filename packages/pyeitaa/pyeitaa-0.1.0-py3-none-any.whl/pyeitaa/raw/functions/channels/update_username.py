from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class UpdateUsername(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x3514b3de``

    Parameters:
        channel: :obj:`InputChannel <pyeitaa.raw.base.InputChannel>`
        username: ``str``

    Returns:
        ``bool``
    """

    __slots__: List[str] = ["channel", "username"]

    ID = 0x3514b3de
    QUALNAME = "functions.channels.UpdateUsername"

    def __init__(self, *, channel: "raw.base.InputChannel", username: str) -> None:
        self.channel = channel  # InputChannel
        self.username = username  # string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        channel = TLObject.read(data)
        
        username = String.read(data)
        
        return UpdateUsername(channel=channel, username=username)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.channel.write())
        
        data.write(String(self.username))
        
        return data.getvalue()

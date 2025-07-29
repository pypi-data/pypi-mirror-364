from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class EditTitle(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x566decd0``

    Parameters:
        channel: :obj:`InputChannel <pyeitaa.raw.base.InputChannel>`
        title: ``str``

    Returns:
        :obj:`Updates <pyeitaa.raw.base.Updates>`
    """

    __slots__: List[str] = ["channel", "title"]

    ID = 0x566decd0
    QUALNAME = "functions.channels.EditTitle"

    def __init__(self, *, channel: "raw.base.InputChannel", title: str) -> None:
        self.channel = channel  # InputChannel
        self.title = title  # string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        channel = TLObject.read(data)
        
        title = String.read(data)
        
        return EditTitle(channel=channel, title=title)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.channel.write())
        
        data.write(String(self.title))
        
        return data.getvalue()

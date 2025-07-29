from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class InviteToChannelLayer84(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0xc7560885``

    Parameters:
        channel: :obj:`InputChannel <pyeitaa.raw.base.InputChannel>`

    Returns:
        :obj:`Updates <pyeitaa.raw.base.Updates>`
    """

    __slots__: List[str] = ["channel"]

    ID = 0xc7560885
    QUALNAME = "functions.channels.InviteToChannelLayer84"

    def __init__(self, *, channel: "raw.base.InputChannel") -> None:
        self.channel = channel  # InputChannel

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        channel = TLObject.read(data)
        
        return InviteToChannelLayer84(channel=channel)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.channel.write())
        
        return data.getvalue()

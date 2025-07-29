from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Bytes
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class ViewSponsoredMessage(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x4151246c``

    Parameters:
        channel: :obj:`InputChannel <pyeitaa.raw.base.InputChannel>`
        random_id: ``bytes``

    Returns:
        ``bool``
    """

    __slots__: List[str] = ["channel", "random_id"]

    ID = -0x4151246c
    QUALNAME = "functions.channels.ViewSponsoredMessage"

    def __init__(self, *, channel: "raw.base.InputChannel", random_id: bytes) -> None:
        self.channel = channel  # InputChannel
        self.random_id = random_id  # bytes

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        channel = TLObject.read(data)
        
        random_id = Bytes.read(data)
        
        return ViewSponsoredMessage(channel=channel, random_id=random_id)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.channel.write())
        
        data.write(Bytes(self.random_id))
        
        return data.getvalue()

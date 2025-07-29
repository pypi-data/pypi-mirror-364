from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class EditPhoto(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0xed1a837``

    Parameters:
        channel: :obj:`InputChannel <pyeitaa.raw.base.InputChannel>`
        photo: :obj:`InputChatPhoto <pyeitaa.raw.base.InputChatPhoto>`

    Returns:
        :obj:`Updates <pyeitaa.raw.base.Updates>`
    """

    __slots__: List[str] = ["channel", "photo"]

    ID = -0xed1a837
    QUALNAME = "functions.channels.EditPhoto"

    def __init__(self, *, channel: "raw.base.InputChannel", photo: "raw.base.InputChatPhoto") -> None:
        self.channel = channel  # InputChannel
        self.photo = photo  # InputChatPhoto

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        channel = TLObject.read(data)
        
        photo = TLObject.read(data)
        
        return EditPhoto(channel=channel, photo=photo)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.channel.write())
        
        data.write(self.photo.write())
        
        return data.getvalue()

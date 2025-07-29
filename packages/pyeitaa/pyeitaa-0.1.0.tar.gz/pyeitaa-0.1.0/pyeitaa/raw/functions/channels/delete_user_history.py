from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class DeleteUserHistory(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x2ef228e5``

    Parameters:
        channel: :obj:`InputChannel <pyeitaa.raw.base.InputChannel>`
        user_id: :obj:`InputUser <pyeitaa.raw.base.InputUser>`

    Returns:
        :obj:`messages.AffectedHistory <pyeitaa.raw.base.messages.AffectedHistory>`
    """

    __slots__: List[str] = ["channel", "user_id"]

    ID = -0x2ef228e5
    QUALNAME = "functions.channels.DeleteUserHistory"

    def __init__(self, *, channel: "raw.base.InputChannel", user_id: "raw.base.InputUser") -> None:
        self.channel = channel  # InputChannel
        self.user_id = user_id  # InputUser

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        channel = TLObject.read(data)
        
        user_id = TLObject.read(data)
        
        return DeleteUserHistory(channel=channel, user_id=user_id)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.channel.write())
        
        data.write(self.user_id.write())
        
        return data.getvalue()

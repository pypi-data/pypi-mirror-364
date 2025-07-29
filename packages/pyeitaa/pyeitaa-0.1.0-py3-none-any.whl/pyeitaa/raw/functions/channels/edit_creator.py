from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class EditCreator(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x70c732e1``

    Parameters:
        channel: :obj:`InputChannel <pyeitaa.raw.base.InputChannel>`
        user_id: :obj:`InputUser <pyeitaa.raw.base.InputUser>`
        password: :obj:`InputCheckPasswordSRP <pyeitaa.raw.base.InputCheckPasswordSRP>`

    Returns:
        :obj:`Updates <pyeitaa.raw.base.Updates>`
    """

    __slots__: List[str] = ["channel", "user_id", "password"]

    ID = -0x70c732e1
    QUALNAME = "functions.channels.EditCreator"

    def __init__(self, *, channel: "raw.base.InputChannel", user_id: "raw.base.InputUser", password: "raw.base.InputCheckPasswordSRP") -> None:
        self.channel = channel  # InputChannel
        self.user_id = user_id  # InputUser
        self.password = password  # InputCheckPasswordSRP

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        channel = TLObject.read(data)
        
        user_id = TLObject.read(data)
        
        password = TLObject.read(data)
        
        return EditCreator(channel=channel, user_id=user_id, password=password)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.channel.write())
        
        data.write(self.user_id.write())
        
        data.write(self.password.write())
        
        return data.getvalue()

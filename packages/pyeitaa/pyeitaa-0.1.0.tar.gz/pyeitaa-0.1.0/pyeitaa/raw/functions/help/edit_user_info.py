from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class EditUserInfo(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x66b91b70``

    Parameters:
        user_id: :obj:`InputUser <pyeitaa.raw.base.InputUser>`
        message: ``str``
        entities: List of :obj:`MessageEntity <pyeitaa.raw.base.MessageEntity>`

    Returns:
        :obj:`help.UserInfo <pyeitaa.raw.base.help.UserInfo>`
    """

    __slots__: List[str] = ["user_id", "message", "entities"]

    ID = 0x66b91b70
    QUALNAME = "functions.help.EditUserInfo"

    def __init__(self, *, user_id: "raw.base.InputUser", message: str, entities: List["raw.base.MessageEntity"]) -> None:
        self.user_id = user_id  # InputUser
        self.message = message  # string
        self.entities = entities  # Vector<MessageEntity>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        user_id = TLObject.read(data)
        
        message = String.read(data)
        
        entities = TLObject.read(data)
        
        return EditUserInfo(user_id=user_id, message=message, entities=entities)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.user_id.write())
        
        data.write(String(self.message))
        
        data.write(Vector(self.entities))
        
        return data.getvalue()

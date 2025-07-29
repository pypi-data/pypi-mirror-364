from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class UserInfo(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.help.UserInfo`.

    Details:
        - Layer: ``135``
        - ID: ``0x1eb3758``

    Parameters:
        message: ``str``
        entities: List of :obj:`MessageEntity <pyeitaa.raw.base.MessageEntity>`
        author: ``str``
        date: ``int`` ``32-bit``

    See Also:
        This object can be returned by 2 methods:

        .. hlist::
            :columns: 2

            - :obj:`help.GetUserInfo <pyeitaa.raw.functions.help.GetUserInfo>`
            - :obj:`help.EditUserInfo <pyeitaa.raw.functions.help.EditUserInfo>`
    """

    __slots__: List[str] = ["message", "entities", "author", "date"]

    ID = 0x1eb3758
    QUALNAME = "types.help.UserInfo"

    def __init__(self, *, message: str, entities: List["raw.base.MessageEntity"], author: str, date: int) -> None:
        self.message = message  # string
        self.entities = entities  # Vector<MessageEntity>
        self.author = author  # string
        self.date = date  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        message = String.read(data)
        
        entities = TLObject.read(data)
        
        author = String.read(data)
        
        date = Int.read(data)
        
        return UserInfo(message=message, entities=entities, author=author, date=date)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(String(self.message))
        
        data.write(Vector(self.entities))
        
        data.write(String(self.author))
        
        data.write(Int(self.date))
        
        return data.getvalue()

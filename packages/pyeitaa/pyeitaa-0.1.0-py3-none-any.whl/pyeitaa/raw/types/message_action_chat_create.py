from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, String, Vector
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class MessageActionChatCreate(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.MessageAction`.

    Details:
        - Layer: ``135``
        - ID: ``-0x42b83453``

    Parameters:
        title: ``str``
        users: List of ``int`` ``64-bit``
    """

    __slots__: List[str] = ["title", "users"]

    ID = -0x42b83453
    QUALNAME = "types.MessageActionChatCreate"

    def __init__(self, *, title: str, users: List[int]) -> None:
        self.title = title  # string
        self.users = users  # Vector<long>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        title = String.read(data)
        
        users = TLObject.read(data, Long)
        
        return MessageActionChatCreate(title=title, users=users)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(String(self.title))
        
        data.write(Vector(self.users, Long))
        
        return data.getvalue()

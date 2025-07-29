from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class CreateChat(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x9cb126e``

    Parameters:
        users: List of :obj:`InputUser <pyeitaa.raw.base.InputUser>`
        title: ``str``

    Returns:
        :obj:`Updates <pyeitaa.raw.base.Updates>`
    """

    __slots__: List[str] = ["users", "title"]

    ID = 0x9cb126e
    QUALNAME = "functions.messages.CreateChat"

    def __init__(self, *, users: List["raw.base.InputUser"], title: str) -> None:
        self.users = users  # Vector<InputUser>
        self.title = title  # string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        users = TLObject.read(data)
        
        title = String.read(data)
        
        return CreateChat(users=users, title=title)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Vector(self.users))
        
        data.write(String(self.title))
        
        return data.getvalue()

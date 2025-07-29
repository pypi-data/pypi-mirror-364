from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, String
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class UpdateUserName(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.Update`.

    Details:
        - Layer: ``135``
        - ID: ``-0x3c0dfd20``

    Parameters:
        user_id: ``int`` ``64-bit``
        first_name: ``str``
        last_name: ``str``
        username: ``str``
    """

    __slots__: List[str] = ["user_id", "first_name", "last_name", "username"]

    ID = -0x3c0dfd20
    QUALNAME = "types.UpdateUserName"

    def __init__(self, *, user_id: int, first_name: str, last_name: str, username: str) -> None:
        self.user_id = user_id  # long
        self.first_name = first_name  # string
        self.last_name = last_name  # string
        self.username = username  # string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        user_id = Long.read(data)
        
        first_name = String.read(data)
        
        last_name = String.read(data)
        
        username = String.read(data)
        
        return UpdateUserName(user_id=user_id, first_name=first_name, last_name=last_name, username=username)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Long(self.user_id))
        
        data.write(String(self.first_name))
        
        data.write(String(self.last_name))
        
        data.write(String(self.username))
        
        return data.getvalue()

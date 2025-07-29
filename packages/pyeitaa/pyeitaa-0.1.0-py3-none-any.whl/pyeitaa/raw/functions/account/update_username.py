from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class UpdateUsername(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x3e0bdd7c``

    Parameters:
        username: ``str``

    Returns:
        :obj:`User <pyeitaa.raw.base.User>`
    """

    __slots__: List[str] = ["username"]

    ID = 0x3e0bdd7c
    QUALNAME = "functions.account.UpdateUsername"

    def __init__(self, *, username: str) -> None:
        self.username = username  # string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        username = String.read(data)
        
        return UpdateUsername(username=username)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(String(self.username))
        
        return data.getvalue()

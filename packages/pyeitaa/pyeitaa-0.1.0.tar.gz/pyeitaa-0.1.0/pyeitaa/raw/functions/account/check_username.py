from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class CheckUsername(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x2714d86c``

    Parameters:
        username: ``str``

    Returns:
        ``bool``
    """

    __slots__: List[str] = ["username"]

    ID = 0x2714d86c
    QUALNAME = "functions.account.CheckUsername"

    def __init__(self, *, username: str) -> None:
        self.username = username  # string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        username = String.read(data)
        
        return CheckUsername(username=username)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(String(self.username))
        
        return data.getvalue()

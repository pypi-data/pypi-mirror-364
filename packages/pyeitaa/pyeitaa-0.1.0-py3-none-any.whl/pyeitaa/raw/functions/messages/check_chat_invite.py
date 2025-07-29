from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class CheckChatInvite(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x3eadb1bb``

    Parameters:
        hash: ``str``

    Returns:
        :obj:`ChatInvite <pyeitaa.raw.base.ChatInvite>`
    """

    __slots__: List[str] = ["hash"]

    ID = 0x3eadb1bb
    QUALNAME = "functions.messages.CheckChatInvite"

    def __init__(self, *, hash: str) -> None:
        self.hash = hash  # string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        hash = String.read(data)
        
        return CheckChatInvite(hash=hash)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(String(self.hash))
        
        return data.getvalue()

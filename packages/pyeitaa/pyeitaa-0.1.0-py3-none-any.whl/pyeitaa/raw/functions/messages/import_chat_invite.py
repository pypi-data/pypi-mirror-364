from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class ImportChatInvite(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x6c50051c``

    Parameters:
        hash: ``str``

    Returns:
        :obj:`Updates <pyeitaa.raw.base.Updates>`
    """

    __slots__: List[str] = ["hash"]

    ID = 0x6c50051c
    QUALNAME = "functions.messages.ImportChatInvite"

    def __init__(self, *, hash: str) -> None:
        self.hash = hash  # string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        hash = String.read(data)
        
        return ImportChatInvite(hash=hash)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(String(self.hash))
        
        return data.getvalue()

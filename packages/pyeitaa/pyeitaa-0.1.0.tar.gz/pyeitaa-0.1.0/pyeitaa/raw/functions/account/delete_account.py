from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class DeleteAccount(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x418d4e0b``

    Parameters:
        reason: ``str``

    Returns:
        ``bool``
    """

    __slots__: List[str] = ["reason"]

    ID = 0x418d4e0b
    QUALNAME = "functions.account.DeleteAccount"

    def __init__(self, *, reason: str) -> None:
        self.reason = reason  # string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        reason = String.read(data)
        
        return DeleteAccount(reason=reason)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(String(self.reason))
        
        return data.getvalue()

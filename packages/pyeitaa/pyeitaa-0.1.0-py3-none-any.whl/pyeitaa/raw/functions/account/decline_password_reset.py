from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class DeclinePasswordReset(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x4c9409f6``

    **No parameters required.**

    Returns:
        ``bool``
    """

    __slots__: List[str] = []

    ID = 0x4c9409f6
    QUALNAME = "functions.account.DeclinePasswordReset"

    def __init__(self) -> None:
        pass

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        return DeclinePasswordReset()

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        return data.getvalue()

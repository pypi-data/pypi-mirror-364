from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class ResetWebAuthorizations(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x682d2594``

    **No parameters required.**

    Returns:
        ``bool``
    """

    __slots__: List[str] = []

    ID = 0x682d2594
    QUALNAME = "functions.account.ResetWebAuthorizations"

    def __init__(self) -> None:
        pass

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        return ResetWebAuthorizations()

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        return data.getvalue()

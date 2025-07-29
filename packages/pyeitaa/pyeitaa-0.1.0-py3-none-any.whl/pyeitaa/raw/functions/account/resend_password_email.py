from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class ResendPasswordEmail(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x7a7f2a15``

    **No parameters required.**

    Returns:
        ``bool``
    """

    __slots__: List[str] = []

    ID = 0x7a7f2a15
    QUALNAME = "functions.account.ResendPasswordEmail"

    def __init__(self) -> None:
        pass

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        return ResendPasswordEmail()

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        return data.getvalue()

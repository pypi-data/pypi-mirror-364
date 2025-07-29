from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class GetWebAuthorizations(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x182e6d6f``

    **No parameters required.**

    Returns:
        :obj:`account.WebAuthorizations <pyeitaa.raw.base.account.WebAuthorizations>`
    """

    __slots__: List[str] = []

    ID = 0x182e6d6f
    QUALNAME = "functions.account.GetWebAuthorizations"

    def __init__(self) -> None:
        pass

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        return GetWebAuthorizations()

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        return data.getvalue()

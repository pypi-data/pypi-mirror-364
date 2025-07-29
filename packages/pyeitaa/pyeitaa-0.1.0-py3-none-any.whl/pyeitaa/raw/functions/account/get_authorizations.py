from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class GetAuthorizations(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x1cdf3ea8``

    **No parameters required.**

    Returns:
        :obj:`account.Authorizations <pyeitaa.raw.base.account.Authorizations>`
    """

    __slots__: List[str] = []

    ID = -0x1cdf3ea8
    QUALNAME = "functions.account.GetAuthorizations"

    def __init__(self) -> None:
        pass

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        return GetAuthorizations()

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        return data.getvalue()

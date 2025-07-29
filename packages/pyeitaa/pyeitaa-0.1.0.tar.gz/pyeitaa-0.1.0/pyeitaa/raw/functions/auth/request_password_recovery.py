from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class RequestPasswordRecovery(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x2768439a``

    **No parameters required.**

    Returns:
        :obj:`auth.PasswordRecovery <pyeitaa.raw.base.auth.PasswordRecovery>`
    """

    __slots__: List[str] = []

    ID = -0x2768439a
    QUALNAME = "functions.auth.RequestPasswordRecovery"

    def __init__(self) -> None:
        pass

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        return RequestPasswordRecovery()

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        return data.getvalue()

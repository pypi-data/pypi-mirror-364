from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class ResetPassword(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x6cf731e5``

    **No parameters required.**

    Returns:
        :obj:`account.ResetPasswordResult <pyeitaa.raw.base.account.ResetPasswordResult>`
    """

    __slots__: List[str] = []

    ID = -0x6cf731e5
    QUALNAME = "functions.account.ResetPassword"

    def __init__(self) -> None:
        pass

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        return ResetPassword()

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        return data.getvalue()

from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class SendVerifyEmailCode(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x7011509f``

    Parameters:
        email: ``str``

    Returns:
        :obj:`account.SentEmailCode <pyeitaa.raw.base.account.SentEmailCode>`
    """

    __slots__: List[str] = ["email"]

    ID = 0x7011509f
    QUALNAME = "functions.account.SendVerifyEmailCode"

    def __init__(self, *, email: str) -> None:
        self.email = email  # string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        email = String.read(data)
        
        return SendVerifyEmailCode(email=email)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(String(self.email))
        
        return data.getvalue()

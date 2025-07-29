from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class SendTwoStepVerificationCode(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x4e24e1cd``

    **No parameters required.**

    Returns:
        :obj:`auth.SentCode <pyeitaa.raw.base.auth.SentCode>`
    """

    __slots__: List[str] = []

    ID = -0x4e24e1cd
    QUALNAME = "functions.SendTwoStepVerificationCode"

    def __init__(self) -> None:
        pass

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        return SendTwoStepVerificationCode()

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        return data.getvalue()

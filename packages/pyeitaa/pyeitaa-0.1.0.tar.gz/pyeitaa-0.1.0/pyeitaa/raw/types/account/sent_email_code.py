from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class SentEmailCode(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.account.SentEmailCode`.

    Details:
        - Layer: ``135``
        - ID: ``-0x7ee07ab1``

    Parameters:
        email_pattern: ``str``
        length: ``int`` ``32-bit``

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`account.SendVerifyEmailCode <pyeitaa.raw.functions.account.SendVerifyEmailCode>`
    """

    __slots__: List[str] = ["email_pattern", "length"]

    ID = -0x7ee07ab1
    QUALNAME = "types.account.SentEmailCode"

    def __init__(self, *, email_pattern: str, length: int) -> None:
        self.email_pattern = email_pattern  # string
        self.length = length  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        email_pattern = String.read(data)
        
        length = Int.read(data)
        
        return SentEmailCode(email_pattern=email_pattern, length=length)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(String(self.email_pattern))
        
        data.write(Int(self.length))
        
        return data.getvalue()

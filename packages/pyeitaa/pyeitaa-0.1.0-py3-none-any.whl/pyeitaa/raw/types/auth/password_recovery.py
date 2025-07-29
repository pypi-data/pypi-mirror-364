from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class PasswordRecovery(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.auth.PasswordRecovery`.

    Details:
        - Layer: ``135``
        - ID: ``0x137948a5``

    Parameters:
        email_pattern: ``str``

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`auth.RequestPasswordRecovery <pyeitaa.raw.functions.auth.RequestPasswordRecovery>`
    """

    __slots__: List[str] = ["email_pattern"]

    ID = 0x137948a5
    QUALNAME = "types.auth.PasswordRecovery"

    def __init__(self, *, email_pattern: str) -> None:
        self.email_pattern = email_pattern  # string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        email_pattern = String.read(data)
        
        return PasswordRecovery(email_pattern=email_pattern)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(String(self.email_pattern))
        
        return data.getvalue()

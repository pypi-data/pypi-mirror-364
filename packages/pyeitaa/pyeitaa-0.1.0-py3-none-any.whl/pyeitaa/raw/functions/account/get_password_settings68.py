from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Bytes
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class GetPasswordSettings68(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x4372ee45``

    Parameters:
        password_hash: ``bytes``

    Returns:
        :obj:`account.PasswordSettings <pyeitaa.raw.base.account.PasswordSettings>`
    """

    __slots__: List[str] = ["password_hash"]

    ID = -0x4372ee45
    QUALNAME = "functions.account.GetPasswordSettings68"

    def __init__(self, *, password_hash: bytes) -> None:
        self.password_hash = password_hash  # bytes

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        password_hash = Bytes.read(data)
        
        return GetPasswordSettings68(password_hash=password_hash)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Bytes(self.password_hash))
        
        return data.getvalue()

from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Bytes
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class ImportLoginToken(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x6a53a31c``

    Parameters:
        token: ``bytes``

    Returns:
        :obj:`auth.LoginToken <pyeitaa.raw.base.auth.LoginToken>`
    """

    __slots__: List[str] = ["token"]

    ID = -0x6a53a31c
    QUALNAME = "functions.auth.ImportLoginToken"

    def __init__(self, *, token: bytes) -> None:
        self.token = token  # bytes

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        token = Bytes.read(data)
        
        return ImportLoginToken(token=token)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Bytes(self.token))
        
        return data.getvalue()

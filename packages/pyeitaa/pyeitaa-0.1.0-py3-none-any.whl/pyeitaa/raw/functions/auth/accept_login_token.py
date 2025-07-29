from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Bytes
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class AcceptLoginToken(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x176b52b3``

    Parameters:
        token: ``bytes``

    Returns:
        :obj:`Authorization <pyeitaa.raw.base.Authorization>`
    """

    __slots__: List[str] = ["token"]

    ID = -0x176b52b3
    QUALNAME = "functions.auth.AcceptLoginToken"

    def __init__(self, *, token: bytes) -> None:
        self.token = token  # bytes

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        token = Bytes.read(data)
        
        return AcceptLoginToken(token=token)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Bytes(self.token))
        
        return data.getvalue()

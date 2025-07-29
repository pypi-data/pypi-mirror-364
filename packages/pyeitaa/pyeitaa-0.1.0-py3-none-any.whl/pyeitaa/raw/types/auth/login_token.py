from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Bytes
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class LoginToken(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.auth.LoginToken`.

    Details:
        - Layer: ``135``
        - ID: ``0x629f1980``

    Parameters:
        expires: ``int`` ``32-bit``
        token: ``bytes``

    See Also:
        This object can be returned by 2 methods:

        .. hlist::
            :columns: 2

            - :obj:`auth.ExportLoginToken <pyeitaa.raw.functions.auth.ExportLoginToken>`
            - :obj:`auth.ImportLoginToken <pyeitaa.raw.functions.auth.ImportLoginToken>`
    """

    __slots__: List[str] = ["expires", "token"]

    ID = 0x629f1980
    QUALNAME = "types.auth.LoginToken"

    def __init__(self, *, expires: int, token: bytes) -> None:
        self.expires = expires  # int
        self.token = token  # bytes

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        expires = Int.read(data)
        
        token = Bytes.read(data)
        
        return LoginToken(expires=expires, token=token)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Int(self.expires))
        
        data.write(Bytes(self.token))
        
        return data.getvalue()

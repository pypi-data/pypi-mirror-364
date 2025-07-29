from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class LoginTokenSuccess(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.auth.LoginToken`.

    Details:
        - Layer: ``135``
        - ID: ``0x390d5c5e``

    Parameters:
        authorization: :obj:`auth.Authorization <pyeitaa.raw.base.auth.Authorization>`

    See Also:
        This object can be returned by 2 methods:

        .. hlist::
            :columns: 2

            - :obj:`auth.ExportLoginToken <pyeitaa.raw.functions.auth.ExportLoginToken>`
            - :obj:`auth.ImportLoginToken <pyeitaa.raw.functions.auth.ImportLoginToken>`
    """

    __slots__: List[str] = ["authorization"]

    ID = 0x390d5c5e
    QUALNAME = "types.auth.LoginTokenSuccess"

    def __init__(self, *, authorization: "raw.base.auth.Authorization") -> None:
        self.authorization = authorization  # auth.Authorization

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        authorization = TLObject.read(data)
        
        return LoginTokenSuccess(authorization=authorization)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.authorization.write())
        
        return data.getvalue()

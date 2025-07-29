from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class Authorization(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.auth.Authorization`.

    Details:
        - Layer: ``135``
        - ID: ``-0x32faf6ea``

    Parameters:
        token: ``str``
        user: :obj:`User <pyeitaa.raw.base.User>`

    See Also:
        This object can be returned by 7 methods:

        .. hlist::
            :columns: 2

            - :obj:`auth.SignUp <pyeitaa.raw.functions.auth.SignUp>`
            - :obj:`auth.SignIn <pyeitaa.raw.functions.auth.SignIn>`
            - :obj:`auth.ImportAuthorization <pyeitaa.raw.functions.auth.ImportAuthorization>`
            - :obj:`auth.ImportBotAuthorization <pyeitaa.raw.functions.auth.ImportBotAuthorization>`
            - :obj:`auth.CheckPassword <pyeitaa.raw.functions.auth.CheckPassword>`
            - :obj:`auth.CheckPassword2 <pyeitaa.raw.functions.auth.CheckPassword2>`
            - :obj:`auth.RecoverPassword <pyeitaa.raw.functions.auth.RecoverPassword>`
    """

    __slots__: List[str] = ["token", "user"]

    ID = -0x32faf6ea
    QUALNAME = "types.auth.Authorization"

    def __init__(self, *, token: str, user: "raw.base.User") -> None:
        self.token = token  # string
        self.user = user  # User

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        token = String.read(data)
        
        user = TLObject.read(data)
        
        return Authorization(token=token, user=user)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        
        data.write(Int(flags))
        
        data.write(String(self.token))
        
        data.write(self.user.write())
        
        return data.getvalue()

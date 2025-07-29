from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class AuthorizationSignUpRequired(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.auth.Authorization`.

    Details:
        - Layer: ``135``
        - ID: ``0x44747e9a``

    Parameters:
        terms_of_service (optional): :obj:`help.TermsOfService <pyeitaa.raw.base.help.TermsOfService>`

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

    __slots__: List[str] = ["terms_of_service"]

    ID = 0x44747e9a
    QUALNAME = "types.auth.AuthorizationSignUpRequired"

    def __init__(self, *, terms_of_service: "raw.base.help.TermsOfService" = None) -> None:
        self.terms_of_service = terms_of_service  # flags.0?help.TermsOfService

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        terms_of_service = TLObject.read(data) if flags & (1 << 0) else None
        
        return AuthorizationSignUpRequired(terms_of_service=terms_of_service)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.terms_of_service is not None else 0
        data.write(Int(flags))
        
        if self.terms_of_service is not None:
            data.write(self.terms_of_service.write())
        
        return data.getvalue()

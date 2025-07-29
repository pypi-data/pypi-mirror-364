from typing import Union
from pyeitaa import raw

Authorization = Union[raw.types.auth.Authorization, raw.types.auth.AuthorizationSignUpRequired]


# noinspection PyRedeclaration
class Authorization:
    """This base type has 2 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`auth.Authorization <pyeitaa.raw.types.auth.Authorization>`
            - :obj:`auth.AuthorizationSignUpRequired <pyeitaa.raw.types.auth.AuthorizationSignUpRequired>`

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

    QUALNAME = "pyeitaa.raw.base.auth.Authorization"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")

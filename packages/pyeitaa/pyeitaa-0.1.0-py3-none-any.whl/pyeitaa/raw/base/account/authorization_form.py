from typing import Union
from pyeitaa import raw

AuthorizationForm = Union[raw.types.account.AuthorizationForm]


# noinspection PyRedeclaration
class AuthorizationForm:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`account.AuthorizationForm <pyeitaa.raw.types.account.AuthorizationForm>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`account.GetAuthorizationForm <pyeitaa.raw.functions.account.GetAuthorizationForm>`
    """

    QUALNAME = "pyeitaa.raw.base.account.AuthorizationForm"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")

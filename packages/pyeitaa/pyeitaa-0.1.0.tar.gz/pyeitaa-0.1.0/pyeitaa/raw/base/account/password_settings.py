from typing import Union
from pyeitaa import raw

PasswordSettings = Union[raw.types.account.PasswordSettings, raw.types.account.PasswordSettings68]


# noinspection PyRedeclaration
class PasswordSettings:
    """This base type has 2 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`account.PasswordSettings <pyeitaa.raw.types.account.PasswordSettings>`
            - :obj:`account.PasswordSettings68 <pyeitaa.raw.types.account.PasswordSettings68>`

    See Also:
        This object can be returned by 2 methods:

        .. hlist::
            :columns: 2

            - :obj:`account.GetPasswordSettings <pyeitaa.raw.functions.account.GetPasswordSettings>`
            - :obj:`account.GetPasswordSettings68 <pyeitaa.raw.functions.account.GetPasswordSettings68>`
    """

    QUALNAME = "pyeitaa.raw.base.account.PasswordSettings"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")

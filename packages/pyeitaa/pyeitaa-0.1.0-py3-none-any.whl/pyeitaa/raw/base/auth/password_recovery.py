from typing import Union
from pyeitaa import raw

PasswordRecovery = Union[raw.types.auth.PasswordRecovery]


# noinspection PyRedeclaration
class PasswordRecovery:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`auth.PasswordRecovery <pyeitaa.raw.types.auth.PasswordRecovery>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`auth.RequestPasswordRecovery <pyeitaa.raw.functions.auth.RequestPasswordRecovery>`
    """

    QUALNAME = "pyeitaa.raw.base.auth.PasswordRecovery"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")

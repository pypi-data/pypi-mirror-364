from typing import Union
from pyeitaa import raw

LoginToken = Union[raw.types.auth.LoginToken, raw.types.auth.LoginTokenMigrateTo, raw.types.auth.LoginTokenSuccess]


# noinspection PyRedeclaration
class LoginToken:
    """This base type has 3 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`auth.LoginToken <pyeitaa.raw.types.auth.LoginToken>`
            - :obj:`auth.LoginTokenMigrateTo <pyeitaa.raw.types.auth.LoginTokenMigrateTo>`
            - :obj:`auth.LoginTokenSuccess <pyeitaa.raw.types.auth.LoginTokenSuccess>`

    See Also:
        This object can be returned by 2 methods:

        .. hlist::
            :columns: 2

            - :obj:`auth.ExportLoginToken <pyeitaa.raw.functions.auth.ExportLoginToken>`
            - :obj:`auth.ImportLoginToken <pyeitaa.raw.functions.auth.ImportLoginToken>`
    """

    QUALNAME = "pyeitaa.raw.base.auth.LoginToken"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")

from typing import Union
from pyeitaa import raw

Password = Union[raw.types.account.NoPassword, raw.types.account.Password]


# noinspection PyRedeclaration
class Password:
    """This base type has 2 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`account.NoPassword <pyeitaa.raw.types.account.NoPassword>`
            - :obj:`account.Password <pyeitaa.raw.types.account.Password>`

    See Also:
        This object can be returned by 2 methods:

        .. hlist::
            :columns: 2

            - :obj:`account.GetPassword <pyeitaa.raw.functions.account.GetPassword>`
            - :obj:`account.GetPasswordLayer68 <pyeitaa.raw.functions.account.GetPasswordLayer68>`
    """

    QUALNAME = "pyeitaa.raw.base.account.Password"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")

from typing import Union
from pyeitaa import raw

UserFull = Union[raw.types.UserFull]


# noinspection PyRedeclaration
class UserFull:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`UserFull <pyeitaa.raw.types.UserFull>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`users.GetFullUser <pyeitaa.raw.functions.users.GetFullUser>`
    """

    QUALNAME = "pyeitaa.raw.base.UserFull"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")

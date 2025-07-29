from typing import Union
from pyeitaa import raw

UserPayHash = Union[raw.types.UserPayHash]


# noinspection PyRedeclaration
class UserPayHash:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`UserPayHash <pyeitaa.raw.types.UserPayHash>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`GetPayHash <pyeitaa.raw.functions.GetPayHash>`
    """

    QUALNAME = "pyeitaa.raw.base.UserPayHash"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")

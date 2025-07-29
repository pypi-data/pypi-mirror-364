from typing import Union
from pyeitaa import raw

BindAuthKeyInner = Union[raw.types.BindAuthKeyInner]


# noinspection PyRedeclaration
class BindAuthKeyInner:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`BindAuthKeyInner <pyeitaa.raw.types.BindAuthKeyInner>`
    """

    QUALNAME = "pyeitaa.raw.base.BindAuthKeyInner"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")

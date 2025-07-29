from typing import Union
from pyeitaa import raw

Password2 = Union[raw.types.account.Password2]


# noinspection PyRedeclaration
class Password2:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`account.Password2 <pyeitaa.raw.types.account.Password2>`
    """

    QUALNAME = "pyeitaa.raw.base.account.Password2"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")

from typing import Union
from pyeitaa import raw

BankCardOpenUrl = Union[raw.types.BankCardOpenUrl]


# noinspection PyRedeclaration
class BankCardOpenUrl:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`BankCardOpenUrl <pyeitaa.raw.types.BankCardOpenUrl>`
    """

    QUALNAME = "pyeitaa.raw.base.BankCardOpenUrl"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")

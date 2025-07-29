from typing import Union
from pyeitaa import raw

CountryCode = Union[raw.types.help.CountryCode]


# noinspection PyRedeclaration
class CountryCode:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`help.CountryCode <pyeitaa.raw.types.help.CountryCode>`
    """

    QUALNAME = "pyeitaa.raw.base.help.CountryCode"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")

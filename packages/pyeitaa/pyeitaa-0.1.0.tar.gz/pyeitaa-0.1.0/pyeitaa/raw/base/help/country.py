from typing import Union
from pyeitaa import raw

Country = Union[raw.types.help.Country]


# noinspection PyRedeclaration
class Country:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`help.Country <pyeitaa.raw.types.help.Country>`
    """

    QUALNAME = "pyeitaa.raw.base.help.Country"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")

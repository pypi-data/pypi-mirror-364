from typing import Union
from pyeitaa import raw

ThemeSettings = Union[raw.types.ThemeSettings]


# noinspection PyRedeclaration
class ThemeSettings:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`ThemeSettings <pyeitaa.raw.types.ThemeSettings>`
    """

    QUALNAME = "pyeitaa.raw.base.ThemeSettings"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")

from typing import Union
from pyeitaa import raw

InputThemeSettings = Union[raw.types.InputThemeSettings]


# noinspection PyRedeclaration
class InputThemeSettings:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`InputThemeSettings <pyeitaa.raw.types.InputThemeSettings>`
    """

    QUALNAME = "pyeitaa.raw.base.InputThemeSettings"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")

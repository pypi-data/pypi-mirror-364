from typing import Union
from pyeitaa import raw

BaseTheme = Union[raw.types.BaseThemeArctic, raw.types.BaseThemeClassic, raw.types.BaseThemeDay, raw.types.BaseThemeNight, raw.types.BaseThemeTinted]


# noinspection PyRedeclaration
class BaseTheme:
    """This base type has 5 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`BaseThemeArctic <pyeitaa.raw.types.BaseThemeArctic>`
            - :obj:`BaseThemeClassic <pyeitaa.raw.types.BaseThemeClassic>`
            - :obj:`BaseThemeDay <pyeitaa.raw.types.BaseThemeDay>`
            - :obj:`BaseThemeNight <pyeitaa.raw.types.BaseThemeNight>`
            - :obj:`BaseThemeTinted <pyeitaa.raw.types.BaseThemeTinted>`
    """

    QUALNAME = "pyeitaa.raw.base.BaseTheme"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")

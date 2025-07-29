from typing import Union
from pyeitaa import raw

Themes = Union[raw.types.account.Themes, raw.types.account.ThemesNotModified]


# noinspection PyRedeclaration
class Themes:
    """This base type has 2 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`account.Themes <pyeitaa.raw.types.account.Themes>`
            - :obj:`account.ThemesNotModified <pyeitaa.raw.types.account.ThemesNotModified>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`account.GetThemes <pyeitaa.raw.functions.account.GetThemes>`
    """

    QUALNAME = "pyeitaa.raw.base.account.Themes"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")

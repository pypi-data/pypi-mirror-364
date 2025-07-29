from typing import Union
from pyeitaa import raw

Theme = Union[raw.types.Theme]


# noinspection PyRedeclaration
class Theme:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`Theme <pyeitaa.raw.types.Theme>`

    See Also:
        This object can be returned by 3 methods:

        .. hlist::
            :columns: 2

            - :obj:`account.CreateTheme <pyeitaa.raw.functions.account.CreateTheme>`
            - :obj:`account.UpdateTheme <pyeitaa.raw.functions.account.UpdateTheme>`
            - :obj:`account.GetTheme <pyeitaa.raw.functions.account.GetTheme>`
    """

    QUALNAME = "pyeitaa.raw.base.Theme"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")

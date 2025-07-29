from typing import Union
from pyeitaa import raw

AppUpdate = Union[raw.types.help.AppUpdate, raw.types.help.NoAppUpdate]


# noinspection PyRedeclaration
class AppUpdate:
    """This base type has 2 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`help.AppUpdate <pyeitaa.raw.types.help.AppUpdate>`
            - :obj:`help.NoAppUpdate <pyeitaa.raw.types.help.NoAppUpdate>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`help.GetAppUpdate <pyeitaa.raw.functions.help.GetAppUpdate>`
    """

    QUALNAME = "pyeitaa.raw.base.help.AppUpdate"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")

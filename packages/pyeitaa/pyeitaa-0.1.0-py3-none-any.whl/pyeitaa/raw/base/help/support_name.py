from typing import Union
from pyeitaa import raw

SupportName = Union[raw.types.help.SupportName]


# noinspection PyRedeclaration
class SupportName:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`help.SupportName <pyeitaa.raw.types.help.SupportName>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`help.GetSupportName <pyeitaa.raw.functions.help.GetSupportName>`
    """

    QUALNAME = "pyeitaa.raw.base.help.SupportName"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")

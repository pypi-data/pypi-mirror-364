from typing import Union
from pyeitaa import raw

Support = Union[raw.types.help.Support]


# noinspection PyRedeclaration
class Support:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`help.Support <pyeitaa.raw.types.help.Support>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`help.GetSupport <pyeitaa.raw.functions.help.GetSupport>`
    """

    QUALNAME = "pyeitaa.raw.base.help.Support"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")

from typing import Union
from pyeitaa import raw

Takeout = Union[raw.types.account.Takeout]


# noinspection PyRedeclaration
class Takeout:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`account.Takeout <pyeitaa.raw.types.account.Takeout>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`account.InitTakeoutSession <pyeitaa.raw.functions.account.InitTakeoutSession>`
    """

    QUALNAME = "pyeitaa.raw.base.account.Takeout"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")

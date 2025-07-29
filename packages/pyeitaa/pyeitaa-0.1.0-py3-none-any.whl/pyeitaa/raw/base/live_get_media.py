from typing import Union
from pyeitaa import raw

LiveGetMedia = Union[raw.types.LiveGetMedia]


# noinspection PyRedeclaration
class LiveGetMedia:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`LiveGetMedia <pyeitaa.raw.types.LiveGetMedia>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`LiveGetMedia <pyeitaa.raw.functions.LiveGetMedia>`
    """

    QUALNAME = "pyeitaa.raw.base.LiveGetMedia"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")

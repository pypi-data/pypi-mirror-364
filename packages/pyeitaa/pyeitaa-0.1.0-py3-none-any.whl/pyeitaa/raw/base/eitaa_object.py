from typing import Union
from pyeitaa import raw

EitaaObject = Union[raw.types.EitaaObject]


# noinspection PyRedeclaration
class EitaaObject:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`EitaaObject <pyeitaa.raw.types.EitaaObject>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`EitaaObject <pyeitaa.raw.functions.EitaaObject>`
    """

    QUALNAME = "pyeitaa.raw.base.EitaaObject"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")

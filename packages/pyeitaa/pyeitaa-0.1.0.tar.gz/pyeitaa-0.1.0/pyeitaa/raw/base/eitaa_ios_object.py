from typing import Union
from pyeitaa import raw

EitaaIosObject = Union[raw.types.EitaaIosObject]


# noinspection PyRedeclaration
class EitaaIosObject:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`EitaaIosObject <pyeitaa.raw.types.EitaaIosObject>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`EitaaIosObject <pyeitaa.raw.functions.EitaaIosObject>`
    """

    QUALNAME = "pyeitaa.raw.base.EitaaIosObject"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")

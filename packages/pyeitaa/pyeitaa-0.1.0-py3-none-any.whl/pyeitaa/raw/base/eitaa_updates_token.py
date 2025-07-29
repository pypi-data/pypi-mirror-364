from typing import Union
from pyeitaa import raw

EitaaUpdatesToken = Union[raw.types.EitaaUpdatesToken]


# noinspection PyRedeclaration
class EitaaUpdatesToken:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`EitaaUpdatesToken <pyeitaa.raw.types.EitaaUpdatesToken>`
    """

    QUALNAME = "pyeitaa.raw.base.EitaaUpdatesToken"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")

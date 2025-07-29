from typing import Union
from pyeitaa import raw

Game = Union[raw.types.Game]


# noinspection PyRedeclaration
class Game:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`Game <pyeitaa.raw.types.Game>`
    """

    QUALNAME = "pyeitaa.raw.base.Game"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")

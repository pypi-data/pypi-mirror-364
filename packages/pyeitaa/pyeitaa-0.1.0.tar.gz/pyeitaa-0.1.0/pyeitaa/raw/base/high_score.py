from typing import Union
from pyeitaa import raw

HighScore = Union[raw.types.HighScore]


# noinspection PyRedeclaration
class HighScore:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`HighScore <pyeitaa.raw.types.HighScore>`
    """

    QUALNAME = "pyeitaa.raw.base.HighScore"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")

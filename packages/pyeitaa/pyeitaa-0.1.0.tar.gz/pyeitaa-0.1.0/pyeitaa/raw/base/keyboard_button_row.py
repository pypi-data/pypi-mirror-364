from typing import Union
from pyeitaa import raw

KeyboardButtonRow = Union[raw.types.KeyboardButtonRow]


# noinspection PyRedeclaration
class KeyboardButtonRow:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`KeyboardButtonRow <pyeitaa.raw.types.KeyboardButtonRow>`
    """

    QUALNAME = "pyeitaa.raw.base.KeyboardButtonRow"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")

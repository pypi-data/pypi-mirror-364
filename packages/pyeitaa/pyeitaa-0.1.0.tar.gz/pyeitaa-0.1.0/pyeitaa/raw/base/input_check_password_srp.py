from typing import Union
from pyeitaa import raw

InputCheckPasswordSRP = Union[raw.types.InputCheckPasswordEmpty, raw.types.InputCheckPasswordSRP]


# noinspection PyRedeclaration
class InputCheckPasswordSRP:
    """This base type has 2 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`InputCheckPasswordEmpty <pyeitaa.raw.types.InputCheckPasswordEmpty>`
            - :obj:`InputCheckPasswordSRP <pyeitaa.raw.types.InputCheckPasswordSRP>`
    """

    QUALNAME = "pyeitaa.raw.base.InputCheckPasswordSRP"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")

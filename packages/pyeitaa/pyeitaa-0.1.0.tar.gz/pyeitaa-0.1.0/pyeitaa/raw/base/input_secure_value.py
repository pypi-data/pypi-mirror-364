from typing import Union
from pyeitaa import raw

InputSecureValue = Union[raw.types.InputSecureValue]


# noinspection PyRedeclaration
class InputSecureValue:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`InputSecureValue <pyeitaa.raw.types.InputSecureValue>`
    """

    QUALNAME = "pyeitaa.raw.base.InputSecureValue"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
